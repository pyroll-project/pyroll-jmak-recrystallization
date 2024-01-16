from pyroll.core import Unit, RollPass, Transport, Hook, Profile

Profile.recrystallization_state = Hook[str]()
"""String identifier classifying the state of recrystallization: either 'full', 'partial' or 'none'."""

Profile.recrystallized_fraction = Hook[float]()
"""Fraction of microstructure which is recrystallized"""


@Profile.recrystallization_state
def recrystallization_state(self: Profile):
    """Function to determine if dynamic recrystallization happened or not
    if return = 'full' -> material is fully recrystallized
    if return = 'partial' -> dynamic recrystallization happened
    if return = 'none' -> dynamic recrystallization didn't happen
    """
    if self.recrystallized_fraction > 1 - self.jmak_parameters.full_recrystallization_threshold:
        return "full"
    elif self.recrystallized_fraction > self.jmak_parameters.full_recrystallization_threshold:
        return "partial"
    else:
        return "none"
