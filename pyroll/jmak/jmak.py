import numpy as np

from pyroll.core import RollPass, Transport, root_hooks
from pyroll.jmak.material_data import *
from pyroll.jmak.config import Config


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
"""Critical strain needed for onset of dynamic recrystallization"""
RollPass.OutProfile.strain_s = Hook[float]()
"""Calculation of strain for steady state flow during dynamic recrystallization"""
RollPass.OutProfile.d_drx = Hook[float]()
"""Grain size of dynamic recrystallized grains"""
RollPass.OutProfile.zener_holomon_parameter = Hook[float]()
"""Zener-Holomon-Parameter"""
RollPass.OutProfile.drx_happened = Hook[float]()
"""Counts whether dynamic recrystallization happened. 
Needed for the transport, to decide whether metadynamic or static RX will happen."""
RollPass.OutProfile.drx_recrystallized = Hook[float]()
"""Fraction of microstructure which is recrystallized"""

# To initialize calculation of the mean grain size
root_hooks.add(RollPass.OutProfile.grain_size)


# Dynamic recrystallization
@RollPass.OutProfile.strain
def eps_drx(self: RollPass.OutProfile):
    """Strain after dynamic recrystallization"""
    recrystallized = self.roll_pass.out_profile.drx_recrystallized

    if recrystallized > self.jmak_parameters.threshold:  # Threshold for full recrystallization
        return 0
    else:
        return (self.roll_pass.in_profile.strain + self.roll_pass.strain) * (1 - recrystallized)


@RollPass.OutProfile.drx_recrystallized
def drx_recrystallized(self: RollPass.OutProfile):
    """Fraction of microstructure which is recrystallized"""
    recrystallized = 1 - np.exp(
        -self.jmak_parameters.p7
        * (
                (self.roll_pass.strain - self.roll_pass.out_profile.strain_crit_drx)
                / (self.roll_pass.out_profile.strain_s - self.roll_pass.out_profile.strain_crit_drx)
        ) ** self.jmak_parameters.p8)
    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 1


@RollPass.OutProfile.strain_crit_drx
def strain_crit_drx(self: RollPass.OutProfile):
    """Calculation of the critical strain needed for the onset of dynamic recrystallization"""
    return (
            self.jmak_parameters.c * self.jmak_parameters.p1
            * (self.roll_pass.in_profile.grain_size ** self.jmak_parameters.p2)
            * (self.roll_pass.out_profile.zener_holomon_parameter ** self.jmak_parameters.p3)
    )


@RollPass.OutProfile.strain_s
def strain_s(self: RollPass.OutProfile):
    """Calculation of strain for steady state flow during dynamic recrystallization"""
    return (
            self.jmak_parameters.p4
            * (self.roll_pass.in_profile.grain_size ** self.jmak_parameters.p5)
            * (self.roll_pass.out_profile.zener_holomon_parameter ** self.jmak_parameters.p6)
    )


@RollPass.OutProfile.d_drx
def d_drx(self: RollPass.OutProfile):
    """Grain size of dynamic recrystallized grains"""
    return (
            self.jmak_parameters.p9
            * (self.roll_pass.out_profile.zener_holomon_parameter ** (- self.jmak_parameters.p10))
    )


@RollPass.OutProfile.grain_size
def d_after_drx(self: RollPass.OutProfile):
    """Grain size after dynamic recrystallization"""
    return self.roll_pass.out_profile.d_drx


# pretty sure that there is a better way
@RollPass.OutProfile.drx_happened
def drx_happened(self: RollPass.OutProfile):
    """Function to determine if dynamic recrystallization happened or not
    if return = 'fully recrystallized' -> material is fully recrystallized
    if return = 'yes' -> dynamic recrystallization happened
    if return = 'no' -> dynamic recrystallization didn't happen
    """
    if self.roll_pass.out_profile.strain == 0:
        return 'fully recrystallized'
    elif (self.roll_pass.in_profile.strain + self.roll_pass.strain) > self.roll_pass.out_profile.strain:
        return 'yes'
    else:
        return 'no'


# Zener-Holomon-Parameter (RollPass)
@RollPass.OutProfile.zener_holomon_parameter
def zener_holomon_parameter(self: RollPass.OutProfile):
    return (
            self.roll_pass.strain_rate
            * np.exp(self.jmak_parameters.q_def / (Config.GAS_CONSTANT * self.roll_pass.out_profile.temperature))
    )


# Hook Definitions Transport
root_hooks.add(Transport.OutProfile.grain_size)  # To initialize calculation of the mean grain size
Transport.OutProfile.mean_temp_transport = Hook[float]()
"""Mean temperature between beginning and end of roll pass"""


# Mean Temperature during Transport
@Transport.OutProfile.mean_temp_transport
def mean_temp_transport(self: Transport.OutProfile):
    """Mean temperature between beginning and end of transport"""
    return (self.transport.in_profile.temperature + self.transport.out_profile.temperature) / 2


# Hook Definitions Transport (MDRX)
Transport.OutProfile.t_0_5_md = Hook[float]()
"""Time needed for half the microstructure to metadynamically recrystallize"""
Transport.OutProfile.d_mdrx = Hook[float]()
"""Grain size of metadynamic recrystallized grains"""
Transport.OutProfile.zener_holomon_parameter = Hook[float]()
"""Zener-Holomon-Parameter of the transport"""
Transport.OutProfile.mdrx_recrystallized = Hook[float]()
"""Fraction of microstructure which is recrystallized"""


# Change in strain during transport
@Transport.OutProfile.strain
def mdrx_or_srx_strain(self: Transport.OutProfile):
    if prev_roll_pass(self.transport).out_profile.drx_happened == 'fully recrystallized':
        self.logger.info("Material is fully recrystallized at the beginning of the transport")
        return 0
    elif prev_roll_pass(self.transport).out_profile.drx_happened == 'yes':
        self.logger.info("Metadynamic recrystallization happened")
        return eps_mdrx(self.transport)
    else:
        self.logger.info("Static recrystallization happened")
        return eps_srx(self.transport)


# Change in grain size during transport
@Transport.OutProfile.grain_size
def mdrx_or_srx_grain_size(self: Transport.OutProfile):
    if prev_roll_pass(self.transport).out_profile.drx_happened == 'fully recrystallized':
        return self.transport.out_profile.grain_growth
    elif prev_roll_pass(self.transport).out_profile.drx_happened == 'yes':
        self.logger.info("Calculation of mean grain size according to equations for metadynamic recrystallization")
        return grain_size_mdrx(self.transport) + self.transport.out_profile.grain_growth
    else:
        self.logger.info("Calculation of mean grain size according to equations for static recrystallization")
        return grain_size_srx(self.transport) + self.transport.out_profile.grain_growth


# Metadynamic Recrystallization
def eps_mdrx(transport):
    """Strain after metadynamic recrystallization"""
    return transport.in_profile.strain * (1 - transport.out_profile.mdrx_recrystallized)


def grain_size_mdrx(transport):
    """Mean grain size after metadynamic recrystallization"""
    return (
            prev_roll_pass(transport).out_profile.d_drx
            + ((prev_roll_pass(transport).out_profile.d_drx - transport.out_profile.d_mdrx)
               * transport.out_profile.mdrx_recrystallized)
    )


@Transport.OutProfile.mdrx_recrystallized
def mdrx_recrystallized(self: Transport.OutProfile):
    """Fraction of microstructure which is recrystallized"""
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
    """Time needed for half the microstructure to metadynamically recrystallize"""
    return (
            self.jmak_parameters.a_md
            * (self.transport.out_profile.zener_holomon_parameter ** self.jmak_parameters.n_zm)
            * np.exp(self.jmak_parameters.q_md / (Config.GAS_CONSTANT * self.transport.out_profile.mean_temp_transport))
    )


@Transport.OutProfile.d_mdrx
def d_mdrx(self: Transport.OutProfile):
    """Mean grain size of metadynamically recrystallized grains"""
    return self.jmak_parameters.p11 * (self.transport.out_profile.zener_holomon_parameter ** - self.jmak_parameters.p12)


@Transport.OutProfile.zener_holomon_parameter
def zener_holomon_parameter(self: Transport.OutProfile):
    strain_rate = prev_roll_pass(self.transport).strain_rate
    return (
            strain_rate
            * np.exp(
        self.jmak_parameters.q_def / (Config.GAS_CONSTANT * self.transport.out_profile.mean_temp_transport)
    )
    )


# Hook Definitions Transport (SRX)
Transport.OutProfile.t_0_5 = Hook[float]()
"""Time needed for half the microstructure to statically recrystallize"""
Transport.OutProfile.d_srx = Hook[float]()
"""Mean grain size of the statically recrystallized grains"""
Transport.OutProfile.srx_recrystallized = Hook[float]()
"""Fraction of microstructure which is recrystallized"""


# Static Recrystallization
def eps_srx(transport):
    """Strain after static recrystallization"""
    return transport.in_profile.strain * (1 - transport.out_profile.srx_recrystallized)


def grain_size_srx(transport):
    """Mean grain size after static recrystallization"""
    return (
            (transport.out_profile.srx_recrystallized ** (4 / 3)) * transport.out_profile.d_srx
            + ((1 - transport.out_profile.srx_recrystallized) ** 2) * transport.in_profile.grain_size
    )


@Transport.OutProfile.srx_recrystallized
def srx_recrystallized(self: Transport.OutProfile):
    """Fraction of microstructure which is recrystallized"""
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
    return (
            self.jmak_parameters.a
            * (self.transport.in_profile.strain ** (- self.jmak_parameters.a1))
            * (strain_rate ** self.jmak_parameters.a2)
            * (self.transport.in_profile.grain_size ** self.jmak_parameters.a3)
            * np.exp(
        self.jmak_parameters.q_srx / (Config.GAS_CONSTANT * self.transport.out_profile.mean_temp_transport)
    )
    )


@Transport.OutProfile.d_srx
def d_srx(self: Transport.OutProfile):
    """Mean grain size of static recrystallized grains"""
    strain_rate = prev_roll_pass(self.transport).strain_rate
    return (
            self.jmak_parameters.b
            * (self.transport.in_profile.strain ** (- self.jmak_parameters.b1))
            * (strain_rate ** (- self.jmak_parameters.b2))
            * (self.transport.in_profile.grain_size ** self.jmak_parameters.b3)
            * np.exp(
        self.jmak_parameters.q_dsrx / (Config.GAS_CONSTANT * self.transport.out_profile.mean_temp_transport)
    )
    )


# Hook Definitions Transport (Grain Growth)
Transport.OutProfile.grain_growth = Hook[float]()
"""Functions to calculate the grain growth depending on type of recrystallization happening beforehand"""


# Grain Growth
@Transport.OutProfile.grain_growth
def grain_growth(self: Transport.OutProfile):
    """Function for grain growth

    - if: microstructure is completely recrystallized -> only grain growth
    - elif: dynamic recrystallization happened -> new starting point: metadynamic recrystallization
    - else: static recrystallization as starting point
    | d_rx: mean grain size after recrystallization
    | duration_left: time left for grain growth after full recrystallization
    """
    if prev_roll_pass(self.transport).out_profile.drx_happened == 'fully recrystallized':
        self.logger.info("Grain growth after dynamic recrystallization")
        d_rx = prev_roll_pass(self.transport).out_profile.d_drx
        duration_left = self.transport.duration
    elif prev_roll_pass(self.transport).out_profile.drx_happened == 'yes':
        self.logger.info("Grain growth after metadynamic recrystallization")
        d_rx = grain_size_mdrx(self.transport)
        duration_left = (
                self.transport.duration
                - ((np.log(1 - self.jmak_parameters.threshold) / np.log(0.5)) ** (1 / self.jmak_parameters.n_md))
                * self.transport.out_profile.t_0_5_md
        )
    else:
        self.logger.info("Grain growth after static recrystallization")
        d_rx = grain_size_srx(self.transport)
        duration_left = (
                self.transport.duration
                - ((
                           (np.log(1 - self.jmak_parameters.threshold) / np.log(0.5)) ** (1 / self.jmak_parameters.n_s)
                   ) * self.transport.out_profile.t_0_5)
        )
    return (
            (
                    d_rx ** self.jmak_parameters.s + self.jmak_parameters.k * duration_left
                    * np.exp(- (self.jmak_parameters.q_grth
                                / (Config.GAS_CONSTANT * self.transport.out_profile.mean_temp_transport)))
            ) ** (1 / self.jmak_parameters.s)
    )
