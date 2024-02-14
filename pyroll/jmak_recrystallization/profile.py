from pyroll.core import Hook, Profile

Profile.recrystallization_state = Hook[str]()
"""String identifier classifying the state of recrystallization: either 'full', 'partial' or 'none'."""

Profile.recrystallized_fraction = Hook[float]()
"""Fraction of microstructure which is recrystallized"""
