import numpy as np

from pyroll.core import RollPass, Transport, root_hooks, Unit
from pyroll.jmak.material_data import *
from pyroll.jmak.config import Config


# Function to access previous roll pass
def prev_roll_pass(self):
    """
        Returns a reference to the first preceding roll pass of this unit in the sequence.
        If the parent of this unit is a roll pass,
        it is considered as the next roll pass, so the preceding of this is searched.

        :raises ValueError: if this unit has no parent unit
    """

    if isinstance(self.parent, RollPass):
        prev = self.parent.prev
    else:
        prev = self.prev

    while True:
        if isinstance(prev, RollPass):
            return prev
        prev = prev.prev


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

# Hook-Definitions RollPass
RollPass.recrystallization_critical_strain = Hook[float]()
"""Critical strain needed for onset of dynamic recrystallization"""

RollPass.recrystallization_steady_state_strain = Hook[float]()
"""Calculation of strain for steady state flow during dynamic recrystallization"""

# To initialize calculation of the mean grain size
root_hooks.add(Unit.OutProfile.grain_size)
root_hooks.add(Unit.OutProfile.recrystallized_fraction)


# Dynamic recrystallization
@RollPass.OutProfile.strain
def roll_pass_out_strain(self: RollPass.OutProfile):
    """Strain after dynamic recrystallization"""
    if self.recrystallization_state == "full":
        return 0

    return (self.roll_pass.in_profile.strain + self.roll_pass.strain) * (
            1 - self.roll_pass.recrystallized_fraction)


@RollPass.OutProfile.recrystallized_fraction
def roll_pass_out_recrystallized_fraction(self: RollPass.OutProfile):
    """Previous recrystallisation is reset in roll passes."""
    return self.roll_pass.recrystallized_fraction


@RollPass.recrystallized_fraction
def roll_pass_recrystallized_fraction(self: RollPass):
    """Fraction of microstructure which is recrystallized"""
    recrystallized = 1 - np.exp(
        -self.in_profile.jmak_parameters.p7
        * (
                (self.in_profile.strain + self.strain - self.recrystallization_critical_strain)
                / (self.recrystallization_steady_state_strain - self.recrystallization_critical_strain)
        ) ** self.in_profile.jmak_parameters.p8
    )
    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 0


@RollPass.recrystallization_critical_strain
def roll_pass_recrystallization_critical_strain(self: RollPass):
    """Calculation of the critical strain needed for the onset of dynamic recrystallization"""
    p = self.in_profile

    return (
            p.jmak_parameters.c * p.jmak_parameters.p1
            * (p.grain_size ** p.jmak_parameters.p2)
            * (self.zener_holomon_parameter ** p.jmak_parameters.p3)
    )


@RollPass.recrystallization_steady_state_strain
def roll_pass_recrystallization_steady_state_strain(self: RollPass):
    """Calculation of strain for steady state flow during dynamic recrystallization"""
    p = self.in_profile

    return (
            p.jmak_parameters.p4
            * (p.grain_size ** p.jmak_parameters.p5)
            * (self.zener_holomon_parameter ** p.jmak_parameters.p6)
    )


@RollPass.recrystallized_grain_size
def roll_pass_recrystallized_grain_size(self: RollPass):
    """Grain size of dynamic recrystallized grains"""
    return (
            self.in_profile.jmak_parameters.p9
            * (self.zener_holomon_parameter ** (- self.in_profile.jmak_parameters.p10))
    )


@RollPass.OutProfile.grain_size
def roll_pass_out_grain_size(self: RollPass.OutProfile):
    """Grain size after dynamic recrystallization"""
    return (
            self.roll_pass.in_profile.grain_size
            + ((self.roll_pass.recrystallized_grain_size - self.roll_pass.in_profile.grain_size)
               * self.roll_pass.recrystallized_fraction)
    )


@Profile.recrystallization_state
def recrystallization_state(self: RollPass.OutProfile):
    """Function to determine if dynamic recrystallization happened or not
    if return = 'full' -> material is fully recrystallized
    if return = 'partial' -> dynamic recrystallization happened
    if return = 'none' -> dynamic recrystallization didn't happen
    """
    if self.recrystallized_fraction > 1 - self.jmak_parameters.threshold:
        return "full"
    elif self.recrystallized_fraction > self.jmak_parameters.threshold:
        return "partial"
    else:
        return "none"


# Zener-Holomon-Parameter (RollPass)
@RollPass.zener_holomon_parameter
def roll_pass_zener_holomon_parameter(self: RollPass):
    p = self.in_profile

    return (
            self.strain_rate
            * np.exp(p.jmak_parameters.q_def / (Config.GAS_CONSTANT * p.temperature))
    )


# Mean Temperature during Transport
def mean_temp_transport(self: Transport):
    """Mean temperature between beginning and end of transport"""
    return (self.in_profile.temperature + self.out_profile.temperature) / 2


Transport.half_recrystallization_time = Hook[float]()
"""Time needed for half the microstructure to metadynamically recrystallize"""

Transport.full_recrystallization_time = Hook[float]()
"""Time needed for half the microstructure to metadynamically recrystallize"""

# Hook Definitions Transport (MDRX)
Transport.recrystallization_mechanism = Hook[str]()
"""String identifying the acting primary recrystallisation mechanism: either 'metadynamic', 'static' or 'none'."""


@Transport.recrystallization_mechanism
def transport_recrystallization_mechanism(self: Transport):
    if self.in_profile.recrystallization_state == 'full':
        return "none"
    elif prev_roll_pass(self).out_profile.recrystallization_state == 'partial':
        return "metadynamic"
    return "static"


# Change in strain during transport
@Transport.OutProfile.strain
def transport_out_strain(self: Transport.OutProfile):
    if self.recrystallization_state == "full":
        return 0

    return self.transport.in_profile.strain * (1 - self.recrystallized_fraction)


# Change in grain size during transport
@Transport.OutProfile.grain_size
def transport_out_grain_size_none(self: Transport.OutProfile):
    t = self.transport
    if t.recrystallization_mechanism == "none":
        return transport_grain_growth(t, t.in_profile.grain_size, t.duration)


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


@Transport.OutProfile.grain_size
def transport_out_grain_size_static(self: Transport.OutProfile):
    t = self.transport
    if t.recrystallization_mechanism == "static":
        grown_in_grain_size = transport_grain_growth(t, t.in_profile.grain_size, t.duration)
        grown_recrystallized_grain_size = transport_grain_growth(t, t.recrystallized_grain_size,
                                                                 t.duration - t.full_recrystallization_time)
        return (
                t.recrystallized_fraction ** (4 / 3) * grown_recrystallized_grain_size
                + (1 - t.recrystallized_fraction) ** 2 * grown_in_grain_size
        )


@Transport.OutProfile.recrystallized_fraction
def transport_out_recrystallized_fraction(self: Transport.OutProfile):
    return self.transport.in_profile.recrystallized_fraction + (
            1 - self.transport.in_profile.recrystallized_fraction) * self.recrystallized_fraction


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
                    self.zener_holomon_parameter ** - self.in_profile.jmak_parameters.p12)


@Transport.zener_holomon_parameter
def transport_zener_holomon_parameter(self: Transport):
    strain_rate = prev_roll_pass(self).strain_rate
    return (
            strain_rate
            * np.exp(self.in_profile.jmak_parameters.q_def / (Config.GAS_CONSTANT * mean_temp_transport(self)))
    )


@Transport.recrystallized_fraction
def transport_recrystallized_fraction_static(self: Transport):
    """Fraction of microstructure which is recrystallized"""
    if self.recrystallization_mechanism == "static":
        recrystallized = 1 - np.exp(
            np.log(0.5)
            * (self.duration / self.half_recrystallization_time)
            ** self.in_profile.jmak_parameters.n_s
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
        strain_rate = prev_roll_pass(self).strain_rate
        return (
                p.jmak_parameters.a
                * p.strain ** (- p.jmak_parameters.a1)
                * strain_rate ** p.jmak_parameters.a2
                * p.grain_size ** p.jmak_parameters.a3
                * np.exp(p.jmak_parameters.q_srx / (Config.GAS_CONSTANT * mean_temp_transport(self)))
        )


@Transport.full_recrystallization_time
def transport_full_recrystallization_time_static(self: Transport):
    """Time needed for half the microstructure to statically recrystallize"""
    if self.recrystallization_mechanism == "static":
        return (
                (np.log(self.in_profile.jmak_parameters.threshold) / np.log(0.5))
                ** (1 / self.in_profile.jmak_parameters.n_s)
                * self.half_recrystallization_time
        )


@Transport.recrystallized_grain_size
def transport_recrystallized_grain_size_static(self: Transport):
    """Mean grain size of static recrystallized grains"""
    if self.recrystallization_mechanism == "static":
        strain_rate = prev_roll_pass(self).strain_rate
        p = self.in_profile
        return (
                p.jmak_parameters.b
                * self.in_profile.strain ** (-p.jmak_parameters.b1)
                * strain_rate ** (-p.jmak_parameters.b2)
                * self.in_profile.grain_size ** p.jmak_parameters.b3
                * np.exp(p.jmak_parameters.q_dsrx / (Config.GAS_CONSTANT * mean_temp_transport(self)))
        )


def transport_grain_growth(transport: Transport, grain_size: float, duration: float):
    if duration < 0:
        return grain_size

    return (
            (grain_size ** transport.in_profile.jmak_parameters.s
             + transport.in_profile.jmak_parameters.k * duration
             * np.exp(-transport.in_profile.jmak_parameters.q_grth / (
                            Config.GAS_CONSTANT * mean_temp_transport(transport))))
            ** (1 / transport.in_profile.jmak_parameters.s)
    )
