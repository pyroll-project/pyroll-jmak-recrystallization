import dataclasses
from pyroll.core import Profile, Hook
from typing import Optional


@dataclasses.dataclass
class JMAKDynamicRecrystallizationParameters:
    k: float
    n: float
    a1: float
    a2: float
    a3: float
    b1: float
    b2: float
    b3: float
    c: float
    d1: float
    d2: float


@dataclasses.dataclass
class JMAKStaticRecrystallizationParameters:
    n: float
    a1: float
    a2: float
    a3: float
    a4: float
    qa: float
    d1: float
    d2: float
    d3: float
    d4: float
    qd: float


@dataclasses.dataclass
class JMAKMetadynamicRecrystallizationParameters:
    n: float
    a1: float
    a2: float
    a3: float
    a4: float
    qa: float
    d1: float
    d2: float


@dataclasses.dataclass
class JMAKGrainGrowthParameters:
    d1: float
    d2: float
    qd: float


@dataclasses.dataclass
class JMAKParameters:
    dynamic_recrystallization: Optional[JMAKDynamicRecrystallizationParameters]
    static_recrystallization: Optional[JMAKStaticRecrystallizationParameters]
    metadynamic_recrystallization: Optional[JMAKMetadynamicRecrystallizationParameters]
    grain_growth: Optional[JMAKGrainGrowthParameters]

    full_recrystallization_threshold: float = 0.05


Profile.jmak_parameters = Hook[JMAKParameters]()

S355 = JMAKParameters(
    JMAKDynamicRecrystallizationParameters(
        c=0.79,
        a1=1.2338e-3,
        a2=0.3007,
        a3=0.1971,
        b1=6.6839e-4,
        b2=0.4506,
        b3=0.2265,
        k=1.4952,
        n=1.7347,
        d1=1072.98,
        d2=-0.1629,
    ),
    JMAKStaticRecrystallizationParameters(
        n=1.505,
        a1=3.7704e-8,
        a2=1.1988,
        a3=-1.003,
        a4=0.1886,
        qa=163457.62,
        d1=0.1953,
        d2=0.7016,
        d3=0.0101,
        d4=1.2052,
        qd=6841.34,
    ),
    JMAKMetadynamicRecrystallizationParameters(
        n=2.038,
        a1=6.9235e-2,
        a2=0,
        a3=0,
        a4=-0.9245,
        qa=248617.4,
        d1=840.57,
        d2=-0.1629,
    ),
    JMAKGrainGrowthParameters(
        d1=6.0,
        d2=1.9144e8,
        qd=30000.0
    )
)


@Profile.jmak_parameters
def jmak_s355j2(self: Profile):
    if self.fits_material("s355") or self.fits_material("s355j2"):
        return S355


@Profile.deformation_activation_energy
def jmak_s355j2(self: Profile):
    if self.fits_material("s355") or self.fits_material("s355j2"):
        return 258435.17


C54SICE6 = JMAKParameters(
    JMAKDynamicRecrystallizationParameters(
        c=0.70,
        a1=1.2338e-3,
        a2=0.1022,
        a3=0.2013,
        b1=2.0731e-3,
        b2=0.0724,
        b3=0.2147,
        k=1.6503,
        n=1.4409,
        d1=3339.98,
        d2=-0.1660,
    ),
    JMAKStaticRecrystallizationParameters(
        n=0.736,
        a1=2.7061e-6,
        a2=2.0313,
        a3=-0.3340,
        a4=0.5438,
        qa=50086.94,
        d1=0.8578,
        d2=0.3356,
        d3=0.0137,
        d4=1.072,
        qd=14359.46,
    ),
    JMAKMetadynamicRecrystallizationParameters(
        n=0.95,
        a1=5.0448e-3,
        a2=0,
        a3=0,
        a4=-0.8523,
        qa=286514.93,
        d1=5329.19,
        d2=-0.1660,
    ),
    JMAKGrainGrowthParameters(
        d1=6.8998,
        d2=3.8637e14,
        qd=50000
    )
)


@Profile.jmak_parameters
def jmak_c54sice6(self: Profile):
    if self.fits_material("C54SiCe6"):
        return C54SICE6


@Profile.deformation_activation_energy
def q_c54sice6(self: Profile):
    if self.fits_material("C54SiCe6"):
        return 291876.66


C20 = JMAKParameters(
    JMAKDynamicRecrystallizationParameters(
        c=0.8987,
        a1=2.1517e-3,
        a2=0.092,
        a3=0.1814,
        b1=5.1143e-4,
        b2=0.5252,
        b3=0.1865,
        k=1.169,
        n=1.5158,
        d1=3552.75,
        d2=-0.1837,
    ),
    JMAKStaticRecrystallizationParameters(
        n=1.4919,
        a1=9.9684e-13,
        a2=0.73206,
        a3=-0.15703,
        a4=3.9289,
        qa=92146.84,
        d1=0.6143,
        d2=0.1017,
        d3=0.0130,
        d4=1.1683,
        qd=5008.18,
    ),
    JMAKMetadynamicRecrystallizationParameters(
        n=1.353,
        a1=7.0757,
        a2=0,
        a3=0,
        a4=-0.5408,
        qa=270024.33,
        d1=4263.30,
        d2=-0.1837,
    ),
    JMAKGrainGrowthParameters(
        d1=7.0,
        d2=6.4047e37,
        qd=655043.37
    )
)


@Profile.jmak_parameters
def jmak_c20(self: Profile):
    if self.fits_material("c20"):
        return C20


@Profile.deformation_activation_energy
def q_c20(self: Profile):
    if self.fits_material("c20"):
        return 278877.95


# C45 = JMAKParameters(
#
# )
