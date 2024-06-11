from pyroll.core import config


@config("PYROLL_JMAK_RECRYSTALLIZATION")
class Config:
    THRESHOLD = 0.05
    """Threshold to consider recrystallization as started or finished."""

    BASE_STRAIN = 0.01
    BASE_STRAIN_RATE = 0.01
