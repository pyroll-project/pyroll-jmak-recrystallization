from pyroll.core import RollPass


@RollPass.OutProfile.strain
def roll_pass_out_strain(self: RollPass.OutProfile):
    """Strain after dynamic recrystallization"""
    if self.recrystallization_state == "full":
        return 0

    return (self.roll_pass.in_profile.strain + self.roll_pass.strain) * (
            1 - self.roll_pass.recrystallized_fraction)


@RollPass.OutProfile.recrystallized_fraction
def roll_pass_out_recrystallized_fraction(self: RollPass.OutProfile):
    """Previous recrystallisation is reset in roll passes."""
    return self.roll_pass.recrystallized_fraction


@RollPass.OutProfile.recrystallization_state
def recrystallization_state(self: RollPass.OutProfile):
    """Function to determine if dynamic recrystallization happened or not
    if return = 'full' -> material is fully recrystallized
    if return = 'partial' -> dynamic recrystallization happened
    if return = 'none' -> dynamic recrystallization didn't happen
    """
    if self.recrystallized_fraction > 1 - self.jmak_parameters.threshold:
        return "full"
    elif self.recrystallized_fraction > self.jmak_parameters.threshold:
        return "partial"
    else:
        return "none"
