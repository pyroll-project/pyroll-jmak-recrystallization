from pyroll.core import config


@config("PYROLL_JMAK_RECRYSTALLIZATION")
class Config:
    THRESHOLD = 0.05
    """Threshold to consider recrystallization as started or finished."""
