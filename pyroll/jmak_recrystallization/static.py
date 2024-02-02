import numpy as np
from pyroll.core import Transport, RollPass

from pyroll.core import Config
from .grain_growth import transport_grain_growth
from .transport import mean_temp_transport


@Transport.OutProfile.grain_size
def transport_out_grain_size_static(self: Transport.OutProfile):
    t = self.transport

    if t.recrystallization_mechanism == "static":
        if t.in_profile.jmak_parameters.static_recrystallization is None:
            return t.in_profile.grain_size

        grown_in_grain_size = transport_grain_growth(t, t.in_profile.grain_size, t.duration)
        grown_recrystallized_grain_size = transport_grain_growth(t, t.recrystallized_grain_size,
                                                                 t.duration - t.full_recrystallization_time)
        return (
                t.recrystallized_fraction ** (4 / 3) * grown_recrystallized_grain_size
                + (1 - t.recrystallized_fraction) ** 2 * grown_in_grain_size
        )


@Transport.recrystallized_fraction
def transport_recrystallized_fraction_static(self: Transport):
    """Fraction of microstructure which is recrystallized"""

    if self.recrystallization_mechanism == "static":
        if self.in_profile.jmak_parameters.static_recrystallization is None:
            return 0

        recrystallized = 1 - np.exp(
            np.log(0.5)
            * (self.duration / self.half_recrystallization_time)
            ** self.in_profile.jmak_parameters.static_recrystallization.n
        )

        if np.isfinite(recrystallized):
            return recrystallized
        else:
            return 0


@Transport.half_recrystallization_time
def transport_half_recrystallization_time_static(self: Transport):
    """Time needed for half the microstructure to statically recrystallize"""
    if self.recrystallization_mechanism == "static":
        p = self.in_profile
        strain_rate = self.prev_of(RollPass).strain_rate
        return (
                p.jmak_parameters.static_recrystallization.a1
                * p.strain ** (- p.jmak_parameters.static_recrystallization.a2)
                * strain_rate ** p.jmak_parameters.static_recrystallization.a3
                * (p.grain_size * 1e6) ** p.jmak_parameters.static_recrystallization.a4
                * np.exp(p.jmak_parameters.static_recrystallization.qa
                         / (Config.UNIVERSAL_GAS_CONSTANT * mean_temp_transport(self)))
        )


@Transport.full_recrystallization_time
def transport_full_recrystallization_time_static(self: Transport):
    """Time needed for half the microstructure to statically recrystallize"""
    if self.recrystallization_mechanism == "static":
        p = self.in_profile
        return (
                (np.log(p.jmak_parameters.full_recrystallization_threshold) / np.log(0.5))
                ** (1 / p.jmak_parameters.static_recrystallization.n)
                * self.half_recrystallization_time
        )


@Transport.recrystallized_grain_size
def transport_recrystallized_grain_size_static(self: Transport):
    """Mean grain size of static recrystallized grains"""
    if self.recrystallization_mechanism == "static":
        p = self.in_profile
        strain_rate = self.prev_of(RollPass).strain_rate
        return (
                p.jmak_parameters.static_recrystallization.d1
                * p.strain ** (-p.jmak_parameters.static_recrystallization.d2)
                * strain_rate ** (-p.jmak_parameters.static_recrystallization.d3)
                * (p.grain_size * 1e6) ** p.jmak_parameters.static_recrystallization.d4
                * np.exp(p.jmak_parameters.static_recrystallization.qd
                         / (Config.UNIVERSAL_GAS_CONSTANT * mean_temp_transport(self)))
        ) / 1e6
