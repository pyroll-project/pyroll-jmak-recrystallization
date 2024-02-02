from pyroll.core import Transport, RollPass, Hook

Transport.half_recrystallization_time = Hook[float]()
"""Time needed for half the microstructure to recrystallize"""

Transport.full_recrystallization_time = Hook[float]()
"""Time needed for half the microstructure to recrystallize"""

Transport.recrystallization_mechanism = Hook[str]()
"""String identifying the acting primary recrystallization mechanism: either 'metadynamic', 'static' or 'none'."""


def mean_temp_transport(self: Transport):
    """Mean temperature between beginning and end of transport"""
    return (self.in_profile.temperature + self.out_profile.temperature) / 2


@Transport.recrystallization_mechanism
def transport_recrystallization_mechanism(self: Transport):
    if self.in_profile.recrystallization_state == 'full':
        return "none"
    elif (self.prev_of(RollPass).out_profile.recrystallization_state == 'partial' and
          self.in_profile.jmak_parameters.metadynamic_recrystallization is not None):
        return "metadynamic"
    return "static"


# Change in strain during transport
@Transport.OutProfile.strain
def transport_out_strain(self: Transport.OutProfile):
    if self.recrystallization_state == "full":
        return 0

    return self.transport.in_profile.strain * (1 - self.recrystallized_fraction)


@Transport.OutProfile.recrystallized_fraction
def transport_out_recrystallized_fraction(self: Transport.OutProfile):
    return self.transport.in_profile.recrystallized_fraction + (
            1 - self.transport.in_profile.recrystallized_fraction) * self.recrystallized_fraction
