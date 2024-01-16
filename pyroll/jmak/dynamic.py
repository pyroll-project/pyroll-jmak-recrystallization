import numpy as np
from pyroll.core import RollPass

from pyroll.jmak import Config


@RollPass.recrystallized_fraction
def roll_pass_recrystallized_fraction(self: RollPass):
    """Fraction of microstructure which is recrystallized"""
    recrystallized = 1 - np.exp(
        -self.in_profile.jmak_parameters.dynamic_recrystallization.p7
        * (
                (self.in_profile.strain + self.strain - self.recrystallization_critical_strain)
                / (self.recrystallization_steady_state_strain - self.recrystallization_critical_strain)
        ) ** self.in_profile.jmak_parameters.dynamic_recrystallization.p8
    )
    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 0


@RollPass.recrystallization_critical_strain
def roll_pass_recrystallization_critical_strain(self: RollPass):
    """Calculation of the critical strain needed for the onset of dynamic recrystallization"""
    p = self.in_profile

    return (
            p.jmak_parameters.dynamic_recrystallization.c * p.jmak_parameters.dynamic_recrystallization.p1
            * (p.grain_size ** p.jmak_parameters.dynamic_recrystallization.p2)
            * (self.zener_holomon_parameter ** p.jmak_parameters.dynamic_recrystallization.p3)
    )


@RollPass.recrystallization_steady_state_strain
def roll_pass_recrystallization_steady_state_strain(self: RollPass):
    """Calculation of strain for steady state flow during dynamic recrystallization"""
    p = self.in_profile

    return (
            p.jmak_parameters.dynamic_recrystallization.p4
            * ((p.grain_size * 1e6) ** p.jmak_parameters.dynamic_recrystallization.p5)
            * (self.zener_holomon_parameter ** p.jmak_parameters.dynamic_recrystallization.p6)
    )


@RollPass.recrystallized_grain_size
def roll_pass_recrystallized_grain_size(self: RollPass):
    """Grain size of dynamic recrystallized grains"""
    return (
            self.in_profile.jmak_parameters.dynamic_recrystallization.p9
            * (self.zener_holomon_parameter ** (- self.in_profile.jmak_parameters.dynamic_recrystallization.p10))
    ) / 1e6


@RollPass.zener_holomon_parameter
def roll_pass_zener_holomon_parameter(self: RollPass):
    p = self.in_profile

    return (
            self.strain_rate
            * np.exp(p.jmak_parameters.dynamic_recrystallization.q_def / (Config.GAS_CONSTANT * p.temperature))
    )
