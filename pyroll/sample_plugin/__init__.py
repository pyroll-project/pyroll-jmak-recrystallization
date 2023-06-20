VERSION = "2.0.0"

from pyroll.core import Profile, Hook

Profile.new_hook = Hook[float]()
"""Define a new hook on profiles."""


@Profile.new_hook
def new_hook_default(self: Profile):
    """A default implementation of the new hook."""
    return 42


@Profile.flow_stress
def a_flow_stress_model(self: Profile):
    """An implementation of an already existing hook."""
    return 21e6
