import numpy as np
from pyroll.core import Unit, Hook, BaseRollPass, Config
from .config import Config as LocalConfig

from .common import average_temperature
from .material_data import JMAKRecrystallizationParameters

Unit.recrystallized_grain_size = Hook[float]()
"""Grain size of dynamic recrystallized grains"""

Unit.recrystallized_fraction = Hook[float]()
"""Fraction of microstructure which recrystallizes in this unit"""

Unit.jmak_recrystallization_parameters = Hook[JMAKRecrystallizationParameters]()
"""Current set of recrystallization parameters active."""

Unit.recrystallization_mechanism = Hook[str]()
"""String identifying the acting primary recrystallization mechanism: either 'dynamic', 'metadynamic', 'static' or 'none'."""


@Unit.OutProfile.recrystallized_fraction
def unit_op_recrystallized_fraction(self: Unit.OutProfile):
    if self.unit.subunits:
        return self.unit.subunits[-1].out_profile.recrystallized_fraction

    return self.unit.in_profile.recrystallized_fraction


@Unit.OutProfile.grain_size
def unit_op_grain_size(self: Unit):
    if self.unit.subunits:
        return self.unit.subunits[-1].out_profile.grain_size

    return self.unit.in_profile.grain_size


@Unit.recrystallized_grain_size
def recrystallized_grain_size(self: Unit):
    p = self.in_profile
    strain_rate = (
        self.strain_rate
        if isinstance(self, BaseRollPass)
        else self.prev_of(BaseRollPass).strain_rate
    )
    return (
        self.jmak_recrystallization_parameters.c1
        * (p.strain + LocalConfig.BASE_STRAIN)
        ** self.jmak_recrystallization_parameters.c2
        * (strain_rate + LocalConfig.BASE_STRAIN_RATE)
        ** self.jmak_recrystallization_parameters.c3
        * (p.grain_size * 1e6) ** self.jmak_recrystallization_parameters.c4
        * np.exp(
            self.jmak_recrystallization_parameters.qc
            / (Config.UNIVERSAL_GAS_CONSTANT * average_temperature(self))
        )
    ) / 1e6


@Unit.Profile.recrystallization_state
def recrystallization_state(self: Unit.Profile):
    """Function to determine if dynamic recrystallization happened or not
    if return = 'full' -> material is fully recrystallized
    if return = 'partial' -> dynamic recrystallization happened
    if return = 'none' -> dynamic recrystallization didn't happen
    """
    if self.recrystallized_fraction > 1 - LocalConfig.THRESHOLD:
        return "full"
    elif self.recrystallized_fraction > LocalConfig.THRESHOLD:
        return "partial"
    else:
        return "none"
