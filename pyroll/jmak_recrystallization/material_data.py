import dataclasses

import numpy as np
from pyroll.core import Profile, Hook, Config
from typing import Optional

LOG_05 = np.log(0.5)


@dataclasses.dataclass
class JMAKRecrystallizationParameters:
    k: float = LOG_05
    """Coefficient of Avrami-term."""
    n: float = 1
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


Profile.jmak_dynamic_recrystallization_parameters = Hook[
    JMAKRecrystallizationParameters
]()
Profile.jmak_metadynamic_recrystallization_parameters = Hook[
    JMAKRecrystallizationParameters
]()
Profile.jmak_static_recrystallization_parameters = Hook[
    JMAKRecrystallizationParameters
]()
Profile.jmak_grain_growth_parameters = Hook[JMAKGrainGrowthParameters]()

S355_DYNAMIC = JMAKRecrystallizationParameters(
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
)
S355_STATIC = JMAKRecrystallizationParameters(
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
)
S355_METADYNAMIC = JMAKRecrystallizationParameters(
    n=2.038,
    b1=6.9235e-2,
    b3=-0.9245,
    qb=248617.4 - 258435.17 * 0.9245,
    c1=840.57,
    c3=-0.1629,
    qc=258435.17 * -0.1629,
)
S355_GRAIN_GROWTH = JMAKGrainGrowthParameters(d1=6.0, d2=1.9144e8, qd=-30000.0)


@Profile.jmak_dynamic_recrystallization_parameters
def jmak_s355j2_dynamic(self: Profile):
    if self.fits_material("s355") or self.fits_material("s355j2"):
        return S355_DYNAMIC


@Profile.jmak_metadynamic_recrystallization_parameters
def jmak_s355j2_metadynamic(self: Profile):
    if self.fits_material("s355") or self.fits_material("s355j2"):
        return S355_METADYNAMIC


@Profile.jmak_static_recrystallization_parameters
def jmak_s355j2_static(self: Profile):
    if self.fits_material("s355") or self.fits_material("s355j2"):
        return S355_STATIC


@Profile.jmak_grain_growth_parameters
def jmak_s355j2_grain_growth(self: Profile):
    if self.fits_material("s355") or self.fits_material("s355j2"):
        return S355_GRAIN_GROWTH


C54SICE6_DYNAMIC = JMAKRecrystallizationParameters(
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
)
C54SICE6_STATIC = JMAKRecrystallizationParameters(
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
)
C54SICE6_METADYNAMIC = JMAKRecrystallizationParameters(
    n=0.95,
    b1=5.0448e-3,
    b3=-0.8523,
    qb=286514.93 - 291876.66 * 0.8523,
    c1=5329.19,
    c3=-0.1660,
    qc=291876.66 * -0.1660,
)
C54SICE6_GRAIN_GROWTH = JMAKGrainGrowthParameters(d1=6.8998, d2=3.8637e14, qd=-50000)


@Profile.jmak_dynamic_recrystallization_parameters
def jmak_c54sice6_dynamic(self: Profile):
    if self.fits_material("c54sice6"):
        return C54SICE6_DYNAMIC


@Profile.jmak_metadynamic_recrystallization_parameters
def jmak_c54sice6_metadynamic(self: Profile):
    if self.fits_material("c54sice6"):
        return C54SICE6_METADYNAMIC


@Profile.jmak_static_recrystallization_parameters
def jmak_c54sice6_static(self: Profile):
    if self.fits_material("c54sice6"):
        return C54SICE6_STATIC


@Profile.jmak_grain_growth_parameters
def jmak_c54sice6_grain_growth(self: Profile):
    if self.fits_material("c54sice6"):
        return C54SICE6_GRAIN_GROWTH


C20_DYNAMIC = JMAKRecrystallizationParameters(
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
)
C20_STATIC = JMAKRecrystallizationParameters(
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
)
C20_METADYNAMIC = JMAKRecrystallizationParameters(
    k=LOG_05,
    n=1.353,
    b1=7.0757,
    b3=-0.5408,
    qb=270024.33 - 278877.95 * 0.5408,
    c1=4263.30,
    c2=-0.1837,
    qc=278877.95 * -0.1837,
)
C20_GRAIN_GROWTH = JMAKGrainGrowthParameters(d1=7.0, d2=6.4047e37, qd=-655043.37)


@Profile.jmak_dynamic_recrystallization_parameters
def jmak_c20_dynamic(self: Profile):
    if self.fits_material("c20"):
        return C20_DYNAMIC


@Profile.jmak_metadynamic_recrystallization_parameters
def jmak_c20_metadynamic(self: Profile):
    if self.fits_material("c20"):
        return C20_METADYNAMIC


@Profile.jmak_static_recrystallization_parameters
def jmak_c20_static(self: Profile):
    if self.fits_material("c20"):
        return C20_STATIC


@Profile.jmak_grain_growth_parameters
def jmak_c54sice6_grain_growth(self: Profile):
    if self.fits_material("c20"):
        return C20_GRAIN_GROWTH


C45_DYNAMIC = JMAKRecrystallizationParameters(
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
)
C45_STATIC = JMAKRecrystallizationParameters(
    n=0.52445,
    b1=0.154,
    b2=-4.6694,
    b3=-0.5013,
    b4=-1.8467,
    qb=103653,
    c1=1.35e-10,
    c2=-1.013,
    c4=0.91,
    qc=312000 * 0.0981,
)
C45_GRAIN_GROWTH = JMAKGrainGrowthParameters(d1=7.4716, d2=1.08e12, qd=46135)


@Profile.jmak_dynamic_recrystallization_parameters
def jmak_c45_dynamic(self: Profile):
    if self.fits_material("c45"):
        return C45_DYNAMIC


@Profile.jmak_static_recrystallization_parameters
def jmak_c45_static(self: Profile):
    if self.fits_material("c45"):
        return C45_STATIC


@Profile.jmak_grain_growth_parameters
def jmak_c54sice6_grain_growth(self: Profile):
    if self.fits_material("c45"):
        return C45_GRAIN_GROWTH


# P. D. Hodgson and R. K. Gibbs,
# “A Mathematical Model to Predict the Mechanical Properties of Hot Rolled C-Mn and Microalloyed Steels.,”
# ISIJ International, vol. 32, no. 12, pp. 1329–1338, 1992, doi: 10.2355/isijinternational.32.1329.
#
# T. M. Maccagno, J. J. Jonas, and P. D. Hodgson,
# “Spreadsheet Modelling of Grain Size Evolution during Rod Rolling.,”
# ISIJ International, vol. 36, no. 6, pp. 720–728, 1996, doi: 10.2355/isijinternational.36.720.
#
# 0.06-0.25% C, 0.3-1.7% Mn, grain size 40-150μm, temperature 850-1000°C, strain 0.3-2.4, strain rate 0.03-3/s
C_MN_DYNAMIC = JMAKRecrystallizationParameters(
    a1=5.6e-4,
    a3=0.17,
    a4=0.3,
    qa=300e3 * 0.17,
    c1=1.6e4,
    c3=-0.23,
    qc=300e3 * -0.23,
)
C_MN_STATIC = JMAKRecrystallizationParameters(
    n=1,
    b1=2.3e-15,
    b2=-2.5,
    b4=1,
    qb=230e3,
    c1=343,
    c2=-0.5,
    c4=0.4,
    qc=-45e3,
)
C_MN_METADYNAMIC = JMAKRecrystallizationParameters(
    n=1.5,
    b1=1.1,
    b3=-0.8,
    qb=230e3 - 300e3 * 0.8,
    c1=2.6e4,
    c3=-0.23,
    qc=300e3 * -0.23,
)
C_MN_GRAIN_GROWTH = JMAKGrainGrowthParameters(d1=7, d2=1.45e27, qd=-400e3)


@Profile.jmak_dynamic_recrystallization_parameters
def jmak_c_MN_dynamic(self: Profile):
    if self.fits_material("c-mn"):
        return C_MN_DYNAMIC


@Profile.jmak_metadynamic_recrystallization_parameters
def jmak_c_MN_metadynamic(self: Profile):
    if self.fits_material("c-mn"):
        return C_MN_METADYNAMIC


@Profile.jmak_static_recrystallization_parameters
def jmak_c_MN_static(self: Profile):
    if self.fits_material("c-mn"):
        return C_MN_STATIC


@Profile.jmak_grain_growth_parameters
def jmak_c54sice6_grain_growth(self: Profile):
    if self.fits_material("c-mn"):
        return C_MN_GRAIN_GROWTH


# F. Bubeck: Charakterisierung und Modellierung der Gefügeentwicklung bei der Warmumformung von Kupferwerkstoffen,
# Diss. IMF TUBAF, 2007, Freiberger Forschungshefte B330
# temperature 600-850°C, grain size 180-850μm, strain 0.1-1.2, strain rate 0.001-20
CUZN30_DYNAMIC = JMAKRecrystallizationParameters(
    n=1.5188,
    a1=9.0722e-5,
    a3=0.17,
    a4=0.32,
    qa=262e3 * 0.37,
    b1=2.15e-3,
    b3=0.2176,
    b4=0.3592,
    qb=2800 * Config.UNIVERSAL_GAS_CONSTANT,
    c1=12134,
    c3=-0.16,
    qc=262e3 * -0.16,
)
CUZN30_STATIC = JMAKRecrystallizationParameters(
    n=1.2,
    b1=6.544e-6,
    b2=-2.042,
    b3=-0.2,
    b4=0.3592,
    qb=88664.54,
    c1=33.9,
    c2=-0.581,
    c3=-0.04823,
    c4=0.3592,
    qc=262e3 * -0.04823,
)
CUZN30_METADYNAMIC = JMAKRecrystallizationParameters(
    n=1,
    b1=1 / LOG_05,
    b2=-0.9,
    b3=0.04562,
    qb=262e3 * 0.04562,
    c1=2.678,
    c2=8.161e10,
    qc=-139109,
)
CUZN30_GRAIN_GROWTH = JMAKGrainGrowthParameters(d1=2.678, d2=8.161e10, qd=-196e3)


@Profile.jmak_dynamic_recrystallization_parameters
def jmak_cuzn30_dynamic(self: Profile):
    if self.fits_material("cuzn30"):
        return CUZN30_DYNAMIC


# @Profile.jmak_metadynamic_recrystallization_parameters
# def jmak_cuzn30_metadynamic(self: Profile):
#     if self.fits_material("cuzn30"):
#         return CUZN30_METADYNAMIC


@Profile.jmak_static_recrystallization_parameters
def jmak_cuzn30_static(self: Profile):
    if self.fits_material("cuzn30"):
        return CUZN30_STATIC


@Profile.jmak_grain_growth_parameters
def jmak_c54sice6_grain_growth(self: Profile):
    if self.fits_material("cuzn30"):
        return CUZN30_GRAIN_GROWTH
