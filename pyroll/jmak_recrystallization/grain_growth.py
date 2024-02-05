import numpy as np
from pyroll.core import Transport

from pyroll.core import Config
from .transport import mean_temp_transport


def transport_grain_growth(transport: Transport, grain_size: float, duration: float):
    if not transport.in_profile.jmak_parameters.grain_growth:
        return grain_size

    if duration < 0:
        return grain_size

    return (
            ((grain_size * 1e6) ** transport.in_profile.jmak_parameters.grain_growth.d1
             + transport.in_profile.jmak_parameters.grain_growth.d2 * duration
             * np.exp(-transport.in_profile.jmak_parameters.grain_growth.qd / (
                            Config.UNIVERSAL_GAS_CONSTANT * mean_temp_transport(transport))))
            ** (1 / transport.in_profile.jmak_parameters.grain_growth.d1)
    ) / 1e6


@Transport.OutProfile.grain_size
def transport_out_grain_size_none(self: Transport.OutProfile):
    t = self.transport
    if t.recrystallization_mechanism == "none":
        return transport_grain_growth(t, t.in_profile.grain_size, t.duration)