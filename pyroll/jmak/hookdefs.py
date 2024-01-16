from pyroll.core import Unit, RollPass, Transport, Hook, Profile

Unit.recrystallized_grain_size = Hook[float]()
"""Grain size of dynamic recrystallized grains"""

Unit.zener_holomon_parameter = Hook[float]()
"""Zener-Holomon-Parameter"""

Profile.recrystallization_state = Hook[str]()
"""String identifier classifying the state of recrystallisation: either 'full', 'partial' or 'none'."""

Profile.recrystallized_fraction = Hook[float]()
"""Fraction of microstructure which is recrystallized"""

Unit.recrystallized_fraction = Hook[float]()
"""Fraction of microstructure which recrystallizes in this unit"""

RollPass.recrystallization_critical_strain = Hook[float]()
"""Critical strain needed for onset of dynamic recrystallization"""

RollPass.recrystallization_steady_state_strain = Hook[float]()
"""Calculation of strain for steady state flow during dynamic recrystallization"""

Transport.half_recrystallization_time = Hook[float]()
"""Time needed for half the microstructure to metadynamically recrystallize"""

Transport.full_recrystallization_time = Hook[float]()
"""Time needed for half the microstructure to metadynamically recrystallize"""

# Hook Definitions Transport (MDRX)
Transport.recrystallization_mechanism = Hook[str]()
"""String identifying the acting primary recrystallisation mechanism: either 'metadynamic', 'static' or 'none'."""
