import dataclasses
import numpy as np

VERSION = "2.0.0"

from pyroll.core import RollPass, Profile, Hook, Transport
from pyroll.material_data import *
from pyroll.config import Config

# Hook-Definitions RollPass
RollPass.OutProfile.strain_crit_drx = Hook[float]()
RollPass.OutProfile.strain_s = Hook[float]()
RollPass.OutProfile.d_drx = Hook[float]()
RollPass.OutProfile.zener_holomon_parameter = Hook[float]()


# Dynamic recrystallization
@RollPass.OutProfile.strain
def eps_drx(self: RollPass.OutProfile):
    """Strain after dynamic recrystallization"""
    recrystallized = 1 - np.exp(
        -self.jmak_parameters.p7
        * (
                (self.roll_pass.strain - self.roll_pass.out_profile.strain_crit_drx)
                / (self.roll_pass.out_profile.strain_s - self.roll_pass.out_profile.strain_crit_drx)
        ) ** self.jmak_parameters.p8)

    if np.isfinite(recrystallized):
        return (self.roll_pass.in_profile.strain + self.roll_pass.strain) * (1 - recrystallized)


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


# Zener-Holomon-Parameter
@RollPass.OutProfile.zener_holomon_parameter
def zener_holomon_parameter(self: RollPass.OutProfile):
    return self.roll_pass.strain_rate \
            * np.exp(self.jmak_parameters.q_def / (Config.GAS_CONSTANT * self.roll_pass.out_profile.temperature))


# Metadynamic Recrystallization
"""still missing"""""

# Hook Definitions Transport
Transport.OutProfile.t_0_5 = Hook[float]()
Transport.OutProfile.d_srx = Hook[float]()

# Static Recrystallization
@Transport.OutProfile.strain
def eps_srx(self: Transport.OutProfile):
    """Strain after static recrystallization"""
    recrystallized = 1 - np.exp(
        -np.log(0.5)
        * (
                self.transport.duration / self.transport.out_profile.t_0_5
        ) ** self.jmak_parameters.n_s)

    if np.isfinite(recrystallized):
        return (self.transport.in_profile.strain + self.transport.strain) * (1 - recrystallized)


@Transport.OutProfile.t_0_5
def t_0_5(self: Transport.OutProfile):
    """Time needed for 50% to recrystallize"""  # Strain_rate is needed
    return self.jmak_parameters.a \
        * (self.transport.in_profile.strain ** (- self.jmak_parameters.a1)) \
        * (self.transport.in_profile.strain_rate ** self.jmak_parameters.a2) \
        * (self.transport.in_profile.grain_size ** self.jmak_parameters.a3) \
        * np.exp(self.jmak_parameters.q_srx / (Config.GAS_CONSTANT * self.transport.in_profile.temperature))  # is this the correct temperature?


@Transport.OutProfile.d_srx
def d_srx(self: Transport.OutProfile):
    """Grain size of static recrystallized grains"""  # Strain_rate is needed
    return self.jmak_parameters.b \
        * (self.transport.in_profile.strain ** (- self.jmak_parameters.b1)) \
        * (self.transport.in_profile.strain_rate ** (- self.jmak_parameters.b2)) \
        * (self.transport.in_profile.grain_size ** self.jmak_parameters.b3) \
        * np.exp(self.jmak_parameters.q_dsrx / (Config.GAS_CONSTANT * self.transport.in_profile.temperature))  # is this the correct temperature?
