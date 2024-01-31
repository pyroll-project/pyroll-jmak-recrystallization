import numpy as np
from pyroll.core import Transport, RollPass

from pyroll.core import Config
from .grain_growth import transport_grain_growth
from .transport import mean_temp_transport


@Transport.OutProfile.grain_size
def transport_out_grain_size_metadynamic(self: Transport.OutProfile):
    t = self.transport

    if t.recrystallization_mechanism == "metadynamic":
        grown_in_grain_size = transport_grain_growth(t, t.in_profile.grain_size, t.duration)
        grown_recrystallized_grain_size = transport_grain_growth(t, t.recrystallized_grain_size,
                                                                 t.duration - t.full_recrystallization_time)

        return (
                grown_in_grain_size
                + ((grown_recrystallized_grain_size - grown_in_grain_size)
                   * t.recrystallized_fraction)
        )


@Transport.recrystallized_fraction
def transport_recrystallized_fraction_metadynamic(self: Transport):
    """Fraction of microstructure which is recrystallized"""
    if self.recrystallization_mechanism == "metadynamic":
        recrystallized = 1 - np.exp(
            np.log(0.5)
            * (self.duration / self.half_recrystallization_time)
            ** self.in_profile.jmak_parameters.metadynamic_recrystallization.n
        )

        if np.isfinite(recrystallized):
            return recrystallized
        else:
            return 0


@Transport.half_recrystallization_time
def transport_half_recrystallization_time_metadynamic(self: Transport):
    """Time needed for half the microstructure to metadynamically recrystallize"""
    if self.recrystallization_mechanism == "metadynamic":
        p = self.in_profile
        rp = self.prev_of(RollPass)

        return (
                p.jmak_parameters.metadynamic_recrystallization.a1
                * p.strain ** p.jmak_parameters.metadynamic_recrystallization.a2
                * (p.grain_size * 1e6) ** p.jmak_parameters.metadynamic_recrystallization.a3
                * rp.zener_holomon_parameter ** p.jmak_parameters.metadynamic_recrystallization.a4
                * np.exp(p.jmak_parameters.metadynamic_recrystallization.qa
                         / (Config.UNIVERSAL_GAS_CONSTANT * mean_temp_transport(self)))
        )


@Transport.full_recrystallization_time
def transport_full_recrystallization_time_metadynamic(self: Transport):
    """Time needed for half the microstructure to metadynamically recrystallize"""
    if self.recrystallization_mechanism == "metadynamic":
        p = self.in_profile

        return (
                (np.log(p.jmak_parameters.full_recrystallization_threshold) / np.log(0.5))
                ** (1 / p.jmak_parameters.metadynamic_recrystallization.n)
                * self.half_recrystallization_time
        )


@Transport.recrystallized_grain_size
def transport_recrystallized_grain_size_metadynamic(self: Transport):
    """Mean grain size of metadynamically recrystallized grains"""
    if self.recrystallization_mechanism == "metadynamic":
        p = self.in_profile
        rp = self.prev_of(RollPass)

        return p.jmak_parameters.metadynamic_recrystallization.d1 * (
                rp.zener_holomon_parameter ** p.jmak_parameters.metadynamic_recrystallization.d2
        ) / 1e6
