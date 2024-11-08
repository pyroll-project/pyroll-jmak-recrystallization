import numpy as np
from pyroll.core import Transport, BaseRollPass, Hook, Config
from .config import Config as LocalConfig

from .common import (
    critical_value_function,
    reference_value_function,
    average_temperature,
)

Transport.recrystallization_critical_time = Hook[float]()
"""Time needed for recrystallization to start."""

Transport.recrystallization_reference_time = Hook[float]()
"""Reference time of recrystallization. Typically time of half recrystallization. Depends on used parameter set."""

Transport.recrystallization_finished_time = Hook[float]()
"""Time needed to finish recrystallization."""


@Transport.recrystallization_mechanism
def transport_recrystallization_mechanism(self: Transport):
    try:
        prev_mechanism = self.prev.recrystallization_mechanism
    except (IndexError, ValueError):
        prev_mechanism = "none"

    if prev_mechanism in ["dynamic", "metadynamic"]:
        if self.in_profile.has_value("jmak_metadynamic_recrystallization_parameters"):
            return "metadynamic"
        self.logger.warning(
            "Conditions for metadynamic recrystallization met, but no coefficients available. "
            "Falling back to static recrystallization."
        )

    elif self.in_profile.recrystallization_state == "full":
        if self.in_profile.has_value("jmak_grain_growth_parameters"):
            return "grain_growth"
        self.logger.warning(
            "No grain growth parameters available. Falling back to no recrystallization."
        )
        return "none"

    if self.in_profile.has_value("jmak_static_recrystallization_parameters"):
        return "static"
    self.logger.warning(
        "No static recrystallization parameters available. Falling back to no recrystallization."
    )
    return "none"


@Transport.jmak_recrystallization_parameters
def transport_jmak_recrystallization_parameters(self: BaseRollPass):
    """Use parameters for metadynamic or static recrystallization in roll passes."""
    if self.recrystallization_mechanism == "metadynamic":
        return self.in_profile.jmak_metadynamic_recrystallization_parameters
    return self.in_profile.jmak_static_recrystallization_parameters


@Transport.OutProfile.strain
def transport_out_strain(self: Transport.OutProfile):
    if self.recrystallization_state == "full":
        return 0

    return self.transport.in_profile.strain * (
        1 - self.transport.recrystallized_fraction
    )


@Transport.OutProfile.recrystallized_fraction
def transport_out_recrystallized_fraction(self: Transport.OutProfile):
    return (
        self.transport.in_profile.recrystallized_fraction
        + (1 - self.transport.in_profile.recrystallized_fraction)
        * self.transport.recrystallized_fraction
    )


@Transport.recrystallization_critical_time
def transport_recrystallization_critical_time(self: Transport):
    """Time needed for half the microstructure to statically recrystallize"""
    return critical_value_function(self, self.prev_of(BaseRollPass).strain_rate)


@Transport.recrystallization_reference_time
def transport_recrystallization_reference_time(self: Transport):
    """Time needed for half the microstructure to statically recrystallize"""
    return reference_value_function(self, self.prev_of(BaseRollPass).strain_rate)


@Transport.OutProfile.grain_size
def transport_out_grain_size(self: Transport.OutProfile):
    t = self.transport

    if t.recrystallization_mechanism == "none":
        return t.in_profile.grain_size

    if t.recrystallization_mechanism == "grain_growth":
        return transport_grain_growth(t, t.in_profile.grain_size, t.duration)

    if not t.has_value("jmak_recrystallization_parameters"):
        return t.in_profile.grain_size

    grown_in_grain_size = transport_grain_growth(t, t.in_profile.grain_size, t.duration)
    grown_recrystallized_grain_size = transport_grain_growth(
        t, t.recrystallized_grain_size, t.duration - t.recrystallization_finished_time
    )
    if t.recrystallization_mechanism == "static":
        d = (
            t.recrystallized_fraction ** (4 / 3) * grown_recrystallized_grain_size
            + (1 - t.recrystallized_fraction) ** 2 * grown_in_grain_size
        )
    else:
        d = grown_in_grain_size + (
            (grown_recrystallized_grain_size - grown_in_grain_size)
            * t.recrystallized_fraction
        )

    if np.isclose(d, 0):
        return self.roll_pass.in_profile.grain_size
    return d


@Transport.recrystallized_fraction
def transport_recrystallized_fraction(self: Transport):
    """Fraction of microstructure which is recrystallized"""
    if self.recrystallization_mechanism == "none":
        return 0

    if self.recrystallization_critical_time > self.recrystallization_reference_time:
        return 0

    virtual_time = (
        self.recrystallization_reference_time - self.recrystallization_critical_time
    ) * (
        np.log(1 - self.in_profile.recrystallized_fraction)
        / self.jmak_recrystallization_parameters.k
    ) ** (
        1 / self.jmak_recrystallization_parameters.n
    ) + self.recrystallization_critical_time

    recrystallized = (
        1
        - np.exp(
            self.jmak_recrystallization_parameters.k
            * (
                (self.duration + virtual_time - self.recrystallization_critical_time)
                / (
                    self.recrystallization_reference_time
                    - self.recrystallization_critical_time
                )
            )
            ** self.jmak_recrystallization_parameters.n
        )
        - self.in_profile.recrystallized_fraction
    )

    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 0


@Transport.recrystallization_critical_time
def transport_recrystallization_critical_time(self: Transport):
    """Calculation of the critical strain needed for the onset of dynamic recrystallization"""
    return critical_value_function(self, self.prev_of(BaseRollPass).strain_rate)


@Transport.recrystallization_reference_time
def transport_recrystallization_reference_time(self: Transport):
    """Calculation of strain for steady state flow during dynamic recrystallization"""
    return reference_value_function(self, self.prev_of(BaseRollPass).strain_rate)


def transport_grain_growth(transport: Transport, grain_size: float, duration: float):
    parameters = transport.in_profile.jmak_grain_growth_parameters
    if not parameters:
        return grain_size

    if duration < 0:
        return grain_size

    return (
        (
            (grain_size * 1e6) ** parameters.d1
            + parameters.d2
            * duration
            * np.exp(
                parameters.qd
                / (Config.UNIVERSAL_GAS_CONSTANT * average_temperature(transport))
            )
        )
        ** (1 / parameters.d1)
    ) / 1e6


@Transport.recrystallization_finished_time
def transport_recrystallization_finished_time(self: Transport):
    p = self.in_profile
    return (
        np.log(LocalConfig.THRESHOLD) / self.jmak_recrystallization_parameters.k
    ) ** (
        1 / self.jmak_recrystallization_parameters.n
    ) * self.recrystallization_reference_time
