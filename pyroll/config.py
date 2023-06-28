from pyroll.core import config


@config("PYROLL_JMAK")
class Config:
    GAS_CONSTANT = 8.31446261815324  # Unit: J / (mol * K)
    """The universal gas constant. New one from 2019(?) was used"""
