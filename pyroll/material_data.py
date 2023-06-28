import dataclasses
from pyroll.core import Profile, Hook


@dataclasses.dataclass
class JMAKParameters:
    q_def: float
    c: float
    p1: float
    p2: float
    p3: float
    p4: float
    p5: float
    p6: float
    p7: float
    p8: float
    p9: float
    p10: float


Profile.jmak_parameters = Hook[JMAKParameters]()


@Profile.jmak_parameters
def c45(self: Profile):
    if "C45" in self.material:
        return JMAKParameters(
            q_def=280203.64,
            c=0.88,
            p1=5.8571e-5,
            p2=0.7612,
            p3=0.1995,
            p4=3.6958e-5,
            p5=0.8994,
            p6=0.2212,
            p7=1.0,
            p8=1.2906,
            p9=3811.84,
            p10=0.1706
        )


@Profile.jmak_parameters
def s355j2(self: Profile):
    if "S355J2" in self.material:
        return JMAKParameters(
            q_def=258435.17,
            c=0.79,
            p1=1.2338e-3,
            p2=0.3007,
            p3=0.1971,
            p4=6.6839e-4,
            p5=0.4506,
            p6=0.2265,
            p7=1.4952,
            p8=1.7347,
            p9=1072.98,
            p10=0.1629
        )

@Profile.jmak_parameters
def c54sice6(self: Profile):
    if "C54SiCe6" in self.material:
        return JMAKParameters(
            q_def=291876.66,
            c=0.70,
            p1=1.2338e-3,
            p2=0.1022,
            p3=0.2013,
            p4=2.0731e-3,
            p5=0.0724,
            p6=0.2147,
            p7=1.6503,
            p8=1.4409,
            p9=3339.98,
            p10=0.1660
        )

@Profile.jmak_parameters
def c20(self: Profile):
    if "C20" in self.material:
        return JMAKParameters(
            q_def=278877.95,
            c=0.8987,
            p1=2.1517e-3,
            p2=0.092,
            p3=0.1814,
            p4=5.1143e-4,
            p5=0.5252,
            p6=0.1865,
            p7=1.169,
            p8=1.5158,
            p9=3552.75,
            p10=0.1837
        )
