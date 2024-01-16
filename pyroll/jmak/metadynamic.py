import numpy as np
from pyroll.core import Transport, RollPass

from . import Config
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
            ** self.in_profile.jmak_parameters.n_md
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
        return (
                p.jmak_parameters.a_md
                * (self.zener_holomon_parameter ** p.jmak_parameters.n_zm)
                * np.exp(p.jmak_parameters.q_md / (Config.GAS_CONSTANT * mean_temp_transport(self)))
        )


@Transport.full_recrystallization_time
def transport_full_recrystallization_time_metadynamic(self: Transport):
    """Time needed for half the microstructure to metadynamically recrystallize"""
    if self.recrystallization_mechanism == "metadynamic":
        return (
                (np.log(self.in_profile.jmak_parameters.threshold) / np.log(0.5))
                ** (1 / self.in_profile.jmak_parameters.n_md)
                * self.half_recrystallization_time
        )


@Transport.recrystallized_grain_size
def transport_recrystallized_grain_size_metadynamic(self: Transport):
    """Mean grain size of metadynamically recrystallized grains"""
    if self.recrystallization_mechanism == "metadynamic":
        return self.in_profile.jmak_parameters.p11 * (
                self.zener_holomon_parameter ** - self.in_profile.jmak_parameters.p12) / 1e6


@Transport.zener_holomon_parameter
def transport_zener_holomon_parameter(self: Transport):
    strain_rate = self.prev_of(RollPass).strain_rate
    return (
            strain_rate
            * np.exp(self.in_profile.jmak_parameters.q_def / (Config.GAS_CONSTANT * mean_temp_transport(self)))
    )
