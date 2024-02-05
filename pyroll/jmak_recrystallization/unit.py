from pyroll.core import Unit, Hook

Unit.recrystallized_grain_size = Hook[float]()
"""Grain size of dynamic recrystallized grains"""

Unit.recrystallized_fraction = Hook[float]()
"""Fraction of microstructure which recrystallizes in this unit"""
