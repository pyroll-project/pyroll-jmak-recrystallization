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
    """Previous recrystallization is reset in roll passes."""
    return self.roll_pass.recrystallized_fraction


@RollPass.OutProfile.grain_size
def roll_pass_out_grain_size(self: RollPass.OutProfile):
    """Grain size after dynamic recrystallization"""
    return (
            self.roll_pass.in_profile.grain_size
            + ((self.roll_pass.recrystallized_grain_size - self.roll_pass.in_profile.grain_size)
               * self.roll_pass.recrystallized_fraction)
    )
