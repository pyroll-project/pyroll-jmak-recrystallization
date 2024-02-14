import numpy as np
from pyroll.core import RollPass, Hook

from .common import critical_value_function, reference_value_function

RollPass.recrystallization_critical_strain = Hook[float]()
"""Critical strain for start of dynamic recrystallization."""

RollPass.recrystallization_reference_strain = Hook[float]()
"""Reference strain of dynamic recrystallization. Typically strain of half recrystallization or strain of steady state. Depends on used parameter set."""


@RollPass.OutProfile.strain
def roll_pass_out_strain(self: RollPass.OutProfile):
    """Strain after dynamic recrystallization"""
    if not self.roll_pass.has_value("jmak_recrystallization_parameters"):
        return None

    if self.recrystallization_state == "full":
        return 0

    return (self.roll_pass.in_profile.strain + self.roll_pass.strain) * (
        1 - self.roll_pass.recrystallized_fraction
    )


@RollPass.OutProfile.recrystallized_fraction
def roll_pass_out_recrystallized_fraction(self: RollPass.OutProfile):
    """Previous recrystallization is reset in roll passes."""
    if not self.roll_pass.has_value("jmak_recrystallization_parameters"):
        return 0

    return self.roll_pass.recrystallized_fraction


@RollPass.OutProfile.grain_size
def roll_pass_out_grain_size(self: RollPass.OutProfile):
    """Grain size after dynamic recrystallization"""
    if not self.roll_pass.has_value("jmak_recrystallization_parameters"):
        return self.roll_pass.in_profile.grain_size

    d = self.roll_pass.in_profile.grain_size + (
        (
            self.roll_pass.recrystallized_grain_size
            - self.roll_pass.in_profile.grain_size
        )
        * self.roll_pass.recrystallized_fraction
    )

    if np.isclose(d, 0):
        return self.roll_pass.in_profile.grain_size
    return d


@RollPass.jmak_recrystallization_parameters
def roll_pass_jmak_recrystallization_parameters(self: RollPass):
    """Use parameters for dynamic recrystallization in roll passes."""
    return self.in_profile.jmak_dynamic_recrystallization_parameters


@RollPass.recrystallization_mechanism
def roll_pass_recrystallization_mechanism(self: RollPass):
    if not self.has_value("jmak_recrystallization_parameters"):
        return None

    if self.in_profile.strain + self.strain > self.recrystallization_critical_strain:
        return "dynamic"
    return "none"


@RollPass.recrystallized_fraction
def roll_pass_recrystallized_fraction(self: RollPass):
    """Fraction of microstructure which is recrystallized"""
    if not self.has_value("jmak_recrystallization_parameters"):
        return 0

    recrystallized = 1 - np.exp(
        self.jmak_recrystallization_parameters.k
        * (
            (
                self.in_profile.strain
                + self.strain
                - self.recrystallization_critical_strain
            )
            / (
                self.recrystallization_reference_strain
                - self.recrystallization_critical_strain
            )
        )
        ** self.jmak_recrystallization_parameters.n
    )
    if np.isfinite(recrystallized) and recrystallized > 0:
        return recrystallized
    else:
        return 0


@RollPass.recrystallization_critical_strain
def roll_pass_recrystallization_critical_strain(self: RollPass):
    """Calculation of the critical strain needed for the onset of dynamic recrystallization"""
    return critical_value_function(self, self.strain_rate)


@RollPass.recrystallization_reference_strain
def roll_pass_recrystallization_recrystallization_reference_strain(self: RollPass):
    """Calculation of strain for steady state flow during dynamic recrystallization"""
    return reference_value_function(self, self.strain_rate)
