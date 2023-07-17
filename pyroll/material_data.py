import dataclasses
from pyroll.core import Profile, Hook


@dataclasses.dataclass
class JMAKParameters:
    # Material data for dynamic recrystallization
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
    # Material data for static recrystallization
    n_s: float
    a: float
    a1: float
    a2: float
    a3: float
    q_srx: float
    b: float
    b1: float
    b2: float
    b3: float
    q_dsrx: float
    # Material data for metadynamic recrystallization
    n_md: float
    a_md: float
    q_md: float
    n_zm: float
    # Material data for grain growth
    p11: float
    p12: float
    s: float
    k: float
    q_grth: float
    # Threshold parameter for a fully recrystallized material, can be changed if necessary
    threshold: float = 0.95


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
            p10=0.1706,

            n_s=1.667,
            a=1.0008e-15,
            a1=2.0190,
            a2=-0.2060,
            a3=3.6818,
            q_srx=155829.40,
            b=28.7130, # value is probably wrong, seems to high in comparison to other materials
            b1=0.3000,
            b2=0.0796,
            b3=0.1746,
            q_dsrx=6445.95,

            n_md=0.93,
            a_md=4.169e-4,
            q_md=463982.3,
            n_zm=-0.5088,

            p11=4574.21,
            p12=0.1706,
            s=5.8316,
            k=7.4816e16,
            q_grth=186166.36
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
            p10=0.1629,

            n_s = 1.505,
            a=3.7704e-8,
            a1=1.1988,
            a2=-1.003,
            a3=0.1886,
            q_srx=163457.62,
            b=0.1953,
            b1=0.7016,
            b2=0.0101,
            b3=1.2052,
            q_dsrx=6841.34,

            n_md=2.038,
            a_md=6.9235e-2,
            q_md=248617.4,
            n_zm=-0.9245,

            p11=840.57,
            p12=0.1629,
            s=6.0,
            k=1.9144e8,
            q_grth=30000.0
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
            p10=0.1660,

            n_s=0.736,
            a=2.7061e-6,
            a1=2.0313,
            a2=-0.3340,
            a3=0.5438,
            q_srx=50086.94,
            b=0.8578,
            b1=0.3356,
            b2=0.0137,
            b3=1.072,
            q_dsrx=14359.46,

            n_md=0.95,
            a_md=5.0448e-3,
            q_md=286514.93,
            n_zm=-0.8523,

            p11=5329.19,
            p12=0.1660,
            s=6.8998,
            k=3.8637e14,
            q_grth=50000
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
            p10=0.1837,

            n_s=1.4919,
            a=9.9684e-13,
            a1=0.73206,
            a2=-0.15703,
            a3=3.9289,
            q_srx=92146.84,
            b=0.6143,
            b1=0.1017,
            b2=0.0130,
            b3=1.1683,
            q_dsrx=5008.18,

            n_md=1.353,
            a_md=7.0757,
            q_md=270024.33,
            n_zm=-0.5408,

            p11=4263.30,
            p12=0.1837,
            s=7.0,
            k=6.4047e37,
            q_grth=655043.37
        )
