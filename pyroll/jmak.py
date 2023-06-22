import dataclasses

import numpy as np

VERSION = "2.0.0"

from pyroll.core import RollPass, Profile, Hook, Transport


@dataclasses.dataclass
class JMAKParameters:
    p7: float
    p8: float
    eps_crit: float
    eps_s: float
    t05: float = 0


Profile.jmak_parameters = Hook[JMAKParameters]()
"""jafhjkfhdsjk"""

RollPass.important_value = Hook[float]()
"""docs"""

@RollPass.important_value
def imp(self: RollPass):
    return 42

@RollPass.OutProfile.strain
def drx(self: RollPass.OutProfile):
    recrystallized = 1 - np.exp(
        -self.jmak_parameters.p7
        * (
                (self.roll_pass.strain - self.jmak_parameters.eps_crit)
                / (self.jmak_parameters.eps_s - self.jmak_parameters.eps_crit)
        ) ** self.jmak_parameters.p8)

    print(self.roll_pass.important_value)

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
