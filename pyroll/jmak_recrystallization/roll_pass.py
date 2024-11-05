import numpy as np
from pyroll.core import BaseRollPass, Hook

from .common import critical_value_function, reference_value_function

BaseRollPass.recrystallization_critical_strain = Hook[float]()
"""Critical strain for start of dynamic recrystallization."""

BaseRollPass.recrystallization_reference_strain = Hook[float]()
"""Reference strain of dynamic recrystallization. Typically strain of half recrystallization or strain of steady state. Depends on used parameter set."""


@BaseRollPass.OutProfile.recrystallized_fraction
def roll_pass_out_recrystallized_fraction(self: BaseRollPass.OutProfile):
    """Previous recrystallization is reset in roll passes."""
    return 0


@BaseRollPass.OutProfile.grain_size
def roll_pass_out_grain_size(self: BaseRollPass.OutProfile):
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


@BaseRollPass.jmak_recrystallization_parameters
def roll_pass_jmak_recrystallization_parameters(self: BaseRollPass):
    """Use parameters for dynamic recrystallization in roll passes."""
    return self.in_profile.jmak_dynamic_recrystallization_parameters


@BaseRollPass.recrystallization_mechanism
def roll_pass_recrystallization_mechanism(self: BaseRollPass):
    if not self.has_value("jmak_recrystallization_parameters"):
        return "none"

    if self.in_profile.strain + self.strain > self.recrystallization_critical_strain:
        return "dynamic"
    return "none"


@BaseRollPass.recrystallized_fraction
def roll_pass_recrystallized_fraction(self: BaseRollPass):
    """Fraction of microstructure which is recrystallized"""
    if not self.recrystallization_mechanism == "dynamic":
        return 0

    if self.recrystallization_critical_strain > self.recrystallization_reference_strain:
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


@BaseRollPass.recrystallization_critical_strain
def roll_pass_recrystallization_critical_strain(self: BaseRollPass):
    """Calculation of the critical strain needed for the onset of dynamic recrystallization"""
    return critical_value_function(self, self.strain_rate)


@BaseRollPass.recrystallization_reference_strain
def roll_pass_recrystallization_recrystallization_reference_strain(self: BaseRollPass):
    """Calculation of strain for steady state flow during dynamic recrystallization"""
    return reference_value_function(self, self.strain_rate)
