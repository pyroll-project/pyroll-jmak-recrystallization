import numpy as np
from pyroll.core import RollPass


@RollPass.recrystallized_fraction
def roll_pass_recrystallized_fraction(self: RollPass):
    """Fraction of microstructure which is recrystallized"""
    recrystallized = 1 - np.exp(
        -self.in_profile.jmak_parameters.dynamic_recrystallization.k
        * (
                (self.in_profile.strain + self.strain - self.recrystallization_critical_strain)
                / (self.recrystallization_steady_state_strain - self.recrystallization_critical_strain)
        ) ** self.in_profile.jmak_parameters.dynamic_recrystallization.n
    )
    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 0


@RollPass.recrystallization_maximum_strain
def roll_pass_recrystallization_critical_strain(self: RollPass):
    """Calculation of the critical strain needed for the onset of dynamic recrystallization"""
    p = self.in_profile

    return (
            p.jmak_parameters.dynamic_recrystallization.a1
            * (p.grain_size ** p.jmak_parameters.dynamic_recrystallization.a2)
            * (self.zener_holomon_parameter ** p.jmak_parameters.dynamic_recrystallization.a3)
    )


@RollPass.recrystallization_critical_strain
def roll_pass_recrystallization_critical_strain(self: RollPass):
    """Calculation of the critical strain needed for the onset of dynamic recrystallization"""
    p = self.in_profile

    return p.jmak_parameters.dynamic_recrystallization.c * self.recrystallization_maximum_strain


@RollPass.recrystallization_steady_state_strain
def roll_pass_recrystallization_steady_state_strain(self: RollPass):
    """Calculation of strain for steady state flow during dynamic recrystallization"""
    p = self.in_profile

    return (
            p.jmak_parameters.dynamic_recrystallization.b1
            * ((p.grain_size * 1e6) ** p.jmak_parameters.dynamic_recrystallization.b2)
            * (self.zener_holomon_parameter ** p.jmak_parameters.dynamic_recrystallization.b3)
    )


@RollPass.recrystallized_grain_size
def roll_pass_recrystallized_grain_size(self: RollPass):
    """Grain size of dynamic recrystallized grains"""
    return (
            self.in_profile.jmak_parameters.dynamic_recrystallization.d1
            * (self.zener_holomon_parameter ** (-self.in_profile.jmak_parameters.dynamic_recrystallization.d2))
    ) / 1e6
