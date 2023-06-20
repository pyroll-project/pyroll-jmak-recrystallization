import dataclasses

import numpy as np

VERSION = "2.0.0"

from pyroll.core import RollPass, Profile, Hook


@dataclasses.dataclass
class JMAKParameters:
    p7: float
    p8: float
    eps_crit: float
    eps_s: float


Profile.jmak_parameters = Hook[JMAKParameters]()


@RollPass.OutProfile.strain
def recrystallized_strain(self: RollPass.OutProfile):
    recrystallized = 1 - np.exp(
        -self.jmak_parameters.p7
        * (
                (self.roll_pass.strain - self.jmak_parameters.eps_crit)
                / (self.jmak_parameters.eps_s - self.jmak_parameters.eps_crit)
        ) ** self.jmak_parameters.p8)

    if np.isfinite(recrystallized):
        return (self.roll_pass.in_profile.strain + self.roll_pass.strain) * (1 - recrystallized)


@Profile.jmak_parameters
def c45(self: Profile):
    if "C45" in self.material:
        return JMAKParameters(
            p7=1,
            p8=1.2906,
            eps_crit=0.2,
            eps_s=0.7,
        )


@Profile.jmak_parameters
def c20(self: Profile):
    if "C20" in self.material:
        return JMAKParameters(
            p7=1,
            p8=1.2906,
            eps_crit=0.6,
            eps_s=0.7,
        )
