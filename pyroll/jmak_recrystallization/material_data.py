import dataclasses

import numpy as np
from pyroll.core import Profile, Hook, Config
from typing import Optional

LOG_05 = np.log(0.5)


@dataclasses.dataclass
class JMAKRecrystallizationParameters:
    k: float = LOG_05
    """Coefficient of Avrami-term."""
    n: float = 0
    """Exponent of Avrami-term."""

    a1: float = 0
    """Coefficient of critical value equation."""
    a2: float = 0
    """Strain exponent of critical value equation."""
    a3: float = 0
    """Strain rate exponent of critical value equation."""
    a4: float = 0
    """Grain size of critical value equation."""
    qa: float = 0
    """Activation energy of critical value equation."""

    b1: float = 0
    """Coefficient of reference value equation."""
    b2: float = 0
    """Strain exponent of reference value equation."""
    b3: float = 0
    """Strain rate exponent of reference value equation."""
    b4: float = 0
    """Grain size of reference value equation."""
    qb: float = 0
    """Activation energy of reference value equation."""

    c1: float = 0
    """Coefficient of grain size equation."""
    c2: float = 0
    """Strain exponent of grain size equation."""
    c3: float = 0
    """Strain rate exponent of grain size equation."""
    c4: float = 0
    """Grain size of grain size equation."""
    qc: float = 0
    """Activation energy of grain size equation."""


@dataclasses.dataclass
class JMAKGrainGrowthParameters:
    d1: float
    """Exponent of grain growth."""
    d2: float
    """Coefficient of grain growth."""
    qd: float
    """Activation energy of grain growth."""


@dataclasses.dataclass
class JMAKParameters:
    dynamic_recrystallization: Optional[JMAKRecrystallizationParameters] = None
    static_recrystallization: Optional[JMAKRecrystallizationParameters] = None
    metadynamic_recrystallization: Optional[JMAKRecrystallizationParameters] = None
    grain_growth: Optional[JMAKGrainGrowthParameters] = None

    full_recrystallization_threshold: float = 0.05


Profile.jmak_parameters = Hook[JMAKParameters]()

S355 = JMAKParameters(
    dynamic_recrystallization=JMAKRecrystallizationParameters(
        k=-1.4952,
        n=1.7347,
        a1=1.2338e-3 * 0.79,
        a3=0.1971,
        a4=0.3007,
        qa=258435.17 * 0.1971,
        b1=6.6839e-4,
        b3=0.2265,
        b4=0.4506,
        qb=258435.17 * 0.2265,
        c1=1072.98,
        c3=-0.1629,
        qc=258435.17 * -0.1629,
    ),
    static_recrystallization=JMAKRecrystallizationParameters(
        n=1.505,
        b1=3.7704e-8,
        b2=-1.1988,
        b3=-1.003,
        b4=-0.1886,
        qb=163457.62,
        c1=0.1953,
        c2=-0.7016,
        c3=-0.0101,
        c4=1.2052,
        qc=6841.34,
    ),
    metadynamic_recrystallization=JMAKRecrystallizationParameters(
        n=2.038,
        b1=6.9235e-2,
        b3=-0.9245,
        qb=248617.4 - 258435.17 * 0.9245,
        c1=840.57,
        c3=-0.1629,
        qc=258435.17 * -0.1629,
    ),
    grain_growth=JMAKGrainGrowthParameters(d1=6.0, d2=1.9144e8, qd=-30000.0),
)


@Profile.jmak_parameters
def jmak_s355j2(self: Profile):
    if self.fits_material("s355") or self.fits_material("s355j2"):
        return S355


C54SICE6 = JMAKParameters(
    dynamic_recrystallization=JMAKRecrystallizationParameters(
        k=-1.6503,
        n=1.4409,
        a1=1.2338e-3 * 0.70,
        a3=0.2013,
        a4=0.1022,
        qa=291876.66 * 0.2013,
        b1=2.0731e-3,
        b3=0.2147,
        b4=0.0724,
        qb=291876.66 * 0.2147,
        c1=3339.98,
        c3=-0.1660,
        qc=291876.66 * -0.1660,
    ),
    static_recrystallization=JMAKRecrystallizationParameters(
        n=0.736,
        b1=2.7061e-6,
        b2=-2.0313,
        b3=-0.3340,
        b4=-0.5438,
        qb=50086.94,
        c1=0.8578,
        c2=-0.3356,
        c3=-0.0137,
        c4=1.072,
        qc=14359.46,
    ),
    metadynamic_recrystallization=JMAKRecrystallizationParameters(
        n=0.95,
        b1=5.0448e-3,
        b3=-0.8523,
        qb=286514.93 - 291876.66 * 0.8523,
        c1=5329.19,
        c3=-0.1660,
        qc=291876.66 * -0.1660,
    ),
    grain_growth=JMAKGrainGrowthParameters(d1=6.8998, d2=3.8637e14, qd=-50000),
)


@Profile.jmak_parameters
def jmak_c54sice6(self: Profile):
    if self.fits_material("C54SiCe6"):
        return C54SICE6


C20 = JMAKParameters(
    dynamic_recrystallization=JMAKRecrystallizationParameters(
        k=-1.169,
        n=1.5158,
        a1=2.1517e-3 * 0.8987,
        a3=0.1814,
        a4=0.092,
        qa=278877.95 * 0.1814,
        b1=5.1143e-4,
        b3=0.1865,
        b4=0.5252,
        qb=278877.95 * 0.1865,
        c1=3552.75,
        c3=-0.1837,
        qc=278877.95 * -0.1837,
    ),
    static_recrystallization=JMAKRecrystallizationParameters(
        n=1.4919,
        b1=9.9684e-13,
        b2=-0.73206,
        b3=-0.15703,
        b4=-3.9289,
        qb=92146.84,
        c1=0.6143,
        c2=-0.1017,
        c3=-0.0130,
        c4=1.1683,
        qc=5008.18,
    ),
    metadynamic_recrystallization=JMAKRecrystallizationParameters(
        k=LOG_05,
        n=1.353,
        b1=7.0757,
        b3=-0.5408,
        qb=270024.33 - 278877.95 * 0.5408,
        c1=4263.30,
        c2=-0.1837,
        qc=278877.95 * -0.1837,
    ),
    grain_growth=JMAKGrainGrowthParameters(d1=7.0, d2=6.4047e37, qd=-655043.37),
)


@Profile.jmak_parameters
def jmak_c20(self: Profile):
    if self.fits_material("c20"):
        return C20


C45 = JMAKParameters(
    dynamic_recrystallization=JMAKRecrystallizationParameters(
        n=2,
        a1=4.9e-4,
        a3=0.15,
        a4=0.5,
        qa=312000 * 0.15,
        b1=0.00115,
        b3=0.05,
        b4=0.28,
        qb=6240 * Config.UNIVERSAL_GAS_CONSTANT,
        c1=35.566,
        c3=-0.2312,
        qc=16969 * -0.2312,
    ),
    static_recrystallization=JMAKRecrystallizationParameters(
        n=0.52445,
        b1=0.154,
        b2=-4.6694,
        b3=-0.5013,
        b4=-1.8467,
        qb=103653,
        c1=1.35e-10,
        c2=-1.013,
        c4=0.91,
        qc=312000 * -0.0981,
    ),
    # metadynamic_recrystallization=JMAKRecrystallizationParameters(
    #     n=1.353,
    #     a1=7.0757,
    #     a2=0,
    #     a3=0,
    #     a4=-0.5408,
    #     qa=270024.33,
    #     d1=4263.30,
    #     d2=-0.1837,
    # ),
    grain_growth=JMAKGrainGrowthParameters(d1=7.4716, d2=1.08e12, qd=46135),
)


@Profile.jmak_parameters
def jmak_c45(self: Profile):
    if self.fits_material("c45"):
        return C45


#
#
# @Profile.deformation_activation_energy
# def q_c45(self: Profile):
#     if self.fits_material("c45"):
#         return 16969
