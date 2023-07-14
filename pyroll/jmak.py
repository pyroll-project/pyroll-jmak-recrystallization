import dataclasses
import numpy as np

VERSION = "2.0.0"

from pyroll.core import RollPass, Hook, Transport, Unit
from pyroll.material_data import *
from pyroll.config import Config

# Main question: are the correct temperatures used?

# Function to access previous roll pass
def prev_roll_pass(self):
    """
        Returns a reference to the first preceding roll pass of this unit in the sequence.
        If the parent of this unit is a roll pass,
        it is considered as the next roll pass, so the preceding of this is searched.

        :raises ValueError: if this unit has no parent unit
    """

    if isinstance(self.parent, RollPass):
        prev = self.parent.prev
    else:
        prev = self.prev

    while True:
        if isinstance(prev, RollPass):
            return prev
        prev = prev.prev


# Hook-Definitions RollPass
RollPass.OutProfile.strain_crit_drx = Hook[float]()
RollPass.OutProfile.strain_s = Hook[float]()
RollPass.OutProfile.d_drx = Hook[float]()
RollPass.OutProfile.zener_holomon_parameter = Hook[float]()
RollPass.OutProfile.drx_happened = Hook[float]()
RollPass.OutProfile.drx_recrystallized = Hook[float]()


# Dynamic recrystallization
@RollPass.OutProfile.strain
def eps_drx(self: RollPass.OutProfile):
    """Strain after dynamic recrystallization"""
    recrystallized = self.roll_pass.out_profile.drx_recrystallized

    if recrystallized > 0.95:  # Threshold for full recrystallization
        return 0.0
    else:
        return (self.roll_pass.in_profile.strain + self.roll_pass.strain) * (1 - recrystallized)

@RollPass.OutProfile.drx_recrystallized
def drx_recrystallized(self: RollPass.OutProfile):
    recrystallized = 1 - np.exp(
        -self.jmak_parameters.p7
        * (
                (self.roll_pass.strain - self.roll_pass.out_profile.strain_crit_drx)
                / (self.roll_pass.out_profile.strain_s - self.roll_pass.out_profile.strain_crit_drx)
        ) ** self.jmak_parameters.p8)
#    recrystallized = np.inf
    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 1

@RollPass.OutProfile.strain_crit_drx
def strain_crit_drx(self: RollPass.OutProfile):
    """Calculation of the critical strain needed for the onset of dynamic recrystallization"""
    return self.jmak_parameters.c * self.jmak_parameters.p1 \
            * (self.roll_pass.in_profile.grain_size ** self.jmak_parameters.p2) \
            * (self.roll_pass.out_profile.zener_holomon_parameter ** self.jmak_parameters.p3)


@RollPass.OutProfile.strain_s
def strain_s(self: RollPass.OutProfile):
    """Calculation of strain for steady state flow during dynamic recrystallization"""
    return self.jmak_parameters.p4 \
            * (self.roll_pass.in_profile.grain_size ** self.jmak_parameters.p5) \
            * (self.roll_pass.out_profile.zener_holomon_parameter ** self.jmak_parameters.p6)

@RollPass.OutProfile.d_drx
def d_drx(self: RollPass.OutProfile):
    """Grain size of dynamic recrystallized grains"""
    return self.jmak_parameters.p9 \
            * (self.roll_pass.out_profile.zener_holomon_parameter ** (- self.jmak_parameters.p10))

@RollPass.OutProfile.grain_size
def d_after_drx(self: RollPass.OutProfile):
    """Grain size after dynamic recrystallization"""
    return self.roll_pass.out_profile.d_drx

# pretty sure that there is a better way
@RollPass.OutProfile.drx_happened
def drx_happened(self: RollPass.OutProfile):
    """function to determine if dynamic recrystallization happened or not
    if return = 1 -> material is fully recrystallized
    if return = 1 -> recrystallization happened
    if return = 0 -> recrystallization didn't happen
    """
    if self.roll_pass.out_profile.strain == 0.0:
        return 1
    elif (self.roll_pass.in_profile.strain + self.roll_pass.strain) > self.roll_pass.out_profile.strain:
        return 0.5
    else:
        return 0

# Zener-Holomon-Parameter (RollPass)
@RollPass.OutProfile.zener_holomon_parameter
def zener_holomon_parameter(self: RollPass.OutProfile):
    return self.roll_pass.strain_rate \
            * np.exp(self.jmak_parameters.q_def / (Config.GAS_CONSTANT * self.roll_pass.out_profile.temperature))


# Hook Definitions Transport (MDRX)
Transport.OutProfile.t_0_5_md = Hook[float]()
Transport.OutProfile.d_mdrx = Hook[float]()
Transport.OutProfile.zener_holomon_parameter = Hook[float]()
Transport.OutProfile.mdrx_recrystallized = Hook[float]()


# Change in strain during transport
@Transport.OutProfile.strain
def mdrx_or_srx_strain(self: Transport.OutProfile):
    if prev_roll_pass(self.transport).out_profile.drx_happened == 1:
        return 0
    elif prev_roll_pass(self.transport).out_profile.drx_happened == 0.5:
        print("mdrx")
        return eps_mdrx(self.transport)
    else:
        print("srx")
        return eps_srx(self.transport)

# Change in grain size during transport
@Transport.OutProfile.grain_size
def mdrx_or_srx_grain_size(self: Transport.OutProfile):
    if prev_roll_pass(self.transport).out_profile.drx_happened == 1:
        return self.transport.out_profile.grain_growth
    if prev_roll_pass(self.transport).out_profile.drx_happened == 0.5:
        print("gs_mdrx")
        return grain_size_mdrx(self.transport) + self.transport.out_profile.grain_growth
    else:
        print("gs_srx")
        return grain_size_srx(self.transport) + self.transport.out_profile.grain_growth

# Metadynamic Recrystallization
def eps_mdrx(transport):
    """Strain after metadynamic recrystallization"""
    return transport.in_profile.strain * (1 - transport.out_profile.mdrx_recrystallized)

def grain_size_mdrx(transport):
    """Mean grain size after metadynamic recrystallization"""
    return prev_roll_pass(transport).out_profile.d_drx \
        + ((prev_roll_pass(transport).out_profile.d_drx - transport.out_profile.d_mdrx)
           * transport.out_profile.mdrx_recrystallized)

@Transport.OutProfile.mdrx_recrystallized
def mdrx_recrystallized(self: Transport.OutProfile):
    recrystallized = 1 - np.exp(
        -np.log(0.5)
        * (
                self.transport.duration / self.transport.out_profile.t_0_5_md
        ) ** self.jmak_parameters.n_md)

    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 1

@Transport.OutProfile.t_0_5_md
def t_0_5_md(self: Transport.OutProfile):
    return self.jmak_parameters.a_md \
        * (self.transport.out_profile.zener_holomon_parameter ** self.jmak_parameters.n_md) \
        * np.exp(self.jmak_parameters.q_md / (Config.GAS_CONSTANT * self.transport.in_profile.temperature))

@Transport.OutProfile.d_mdrx
def d_mdrx(self: Transport.OutProfile):
    return self.jmak_parameters.p11 * (self.transport.out_profile.zener_holomon_parameter ** - self.jmak_parameters.p12)


@Transport.OutProfile.zener_holomon_parameter
def zener_holomon_parameter(self: Transport.OutProfile):
    strain_rate = prev_roll_pass(self.transport).strain_rate
    return strain_rate \
            * np.exp(self.jmak_parameters.q_def / (Config.GAS_CONSTANT * self.transport.in_profile.temperature))


# Hook Definitions Transport (SRX)
Transport.OutProfile.t_0_5 = Hook[float]()
Transport.OutProfile.d_srx = Hook[float]()
Transport.OutProfile.srx_recrystallized = Hook[float]()

# Static Recrystallization
def eps_srx(transport):
    """Strain after static recrystallization"""
    return transport.in_profile.strain * (1 - transport.out_profile.srx_recrystallized)

def grain_size_srx(transport):
    return (transport.out_profile.srx_recrystallized ** (4/3)) * transport.out_profile.d_srx \
        + ((1 - transport.out_profile.srx_recrystallized) ** 2) * transport.in_profile.grain_size


@Transport.OutProfile.srx_recrystallized
def srx_recrystallized(self: Transport.OutProfile):
    recrystallized = 1 - np.exp(
        -np.log(0.5)
        * (
                self.transport.duration / self.transport.out_profile.t_0_5
        ) ** self.jmak_parameters.n_s)

    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 1

@Transport.OutProfile.t_0_5
def t_0_5(self: Transport.OutProfile):
    """Time needed for 50% to recrystallize"""
    strain_rate = prev_roll_pass(self.transport).strain_rate
    return self.jmak_parameters.a \
        * (self.transport.in_profile.strain ** (- self.jmak_parameters.a1)) \
        * (strain_rate ** self.jmak_parameters.a2) \
        * (self.transport.in_profile.grain_size ** self.jmak_parameters.a3) \
        * np.exp(self.jmak_parameters.q_srx / (Config.GAS_CONSTANT * self.transport.in_profile.temperature))


@Transport.OutProfile.d_srx
def d_srx(self: Transport.OutProfile):
    """Grain size of static recrystallized grains"""
    strain_rate = prev_roll_pass(self.transport).strain_rate
    return self.jmak_parameters.b \
        * (self.transport.in_profile.strain ** (- self.jmak_parameters.b1)) \
        * (strain_rate ** (- self.jmak_parameters.b2)) \
        * (self.transport.in_profile.grain_size ** self.jmak_parameters.b3) \
        * np.exp(self.jmak_parameters.q_dsrx / (Config.GAS_CONSTANT * self.transport.in_profile.temperature))


# Hook Definitions Transport (Grain Growth)
Transport.OutProfile.grain_growth = Hook[float]()

# Grain Growth
@Transport.OutProfile.grain_growth
def grain_growth(self: Transport.OutProfile):
    """Function for grain growth"""
    if prev_roll_pass(self.transport).out_profile.drx_happened == 1:
        print("gs_growth")
        d_rx = prev_roll_pass(self.transport).out_profile.d_drx
        duration_left = self.transport.duration
    elif prev_roll_pass(self.transport).out_profile.drx_happened == 0.5:
        print("gs_mdrx")
        d_rx = grain_size_mdrx(self.transport)
        duration_left = self.transport.duration \
                        - ((np.log(0.05)/np.log(0.5)) ** (1 / self.jmak_parameters.n_md)) \
                        * self.transport.out_profile.t_0_5_md
    else:
        print("gs_srx")
        d_rx = grain_size_srx(self.transport)
        duration_left = self.transport.duration \
                        - ((np.log(0.05)/np.log(0.5)) ** (1 / self.jmak_parameters.n_s)) \
                        * self.transport.out_profile.t_0_5
    return d_rx ** self.jmak_parameters.s + self.jmak_parameters.k * duration_left \
        * np.exp(- (self.jmak_parameters.q_grth / (Config.GAS_CONSTANT * self.transport.in_profile.temperature)))
