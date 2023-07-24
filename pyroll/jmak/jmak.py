import numpy as np

from pyroll.core import RollPass, Transport, root_hooks
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


# Hook-Definitions RollPass
RollPass.recrystallization_critical_strain = Hook[float]()
"""Critical strain needed for onset of dynamic recrystallization"""

RollPass.recrystallization_steady_state_strain = Hook[float]()
"""Calculation of strain for steady state flow during dynamic recrystallization"""

RollPass.OutProfile.recrystallized_grain_size = Hook[float]()
"""Grain size of dynamic recrystallized grains"""

RollPass.zener_holomon_parameter = Hook[float]()
"""Zener-Holomon-Parameter"""

RollPass.OutProfile.recrystallization_state = Hook[str]()
"""Counts whether dynamic recrystallization happened. 
Needed for the transport, to decide whether metadynamic or static RX will happen."""

RollPass.OutProfile.recrystallized_fraction = Hook[float]()
"""Fraction of microstructure which is recrystallized"""

# To initialize calculation of the mean grain size
root_hooks.add(RollPass.OutProfile.grain_size)


# Dynamic recrystallization
@RollPass.OutProfile.strain
def roll_pass_out_strain(self: RollPass.OutProfile):
    """Strain after dynamic recrystallization"""
    return (self.roll_pass.in_profile.strain + self.roll_pass.strain) * (
            1 - self.roll_pass.out_profile.recrystallized_fraction)


@RollPass.OutProfile.recrystallized_fraction
def roll_pass_out_recrystallized_fraction(self: RollPass.OutProfile):
    """Fraction of microstructure which is recrystallized"""
    rp = self.roll_pass

    recrystallized = 1 - np.exp(
        -self.jmak_parameters.p7
        * (
                (rp.in_profile.strain + rp.strain - rp.recrystallization_critical_strain)
                / (rp.recrystallization_steady_state_strain - rp.recrystallization_critical_strain)
        ) ** self.jmak_parameters.p8
    )
    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 1


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


@RollPass.OutProfile.recrystallized_grain_size
def roll_pass_out_recrystallized_grain_size(self: RollPass.OutProfile):
    """Grain size of dynamic recrystallized grains"""
    return (
            self.jmak_parameters.p9
            * (self.roll_pass.zener_holomon_parameter ** (- self.jmak_parameters.p10))
    )


@RollPass.OutProfile.grain_size
def roll_pass_out_grain_size(self: RollPass.OutProfile):
    """Grain size after dynamic recrystallization"""
    return (
            self.roll_pass.in_profile.grain_size
            + ((self.recrystallized_grain_size - self.roll_pass.in_profile.grain_size)
               * self.recrystallized_fraction)
    )


# pretty sure that there is a better way
@RollPass.OutProfile.recrystallization_state
def roll_pass_out_recrystallization_state(self: RollPass.OutProfile):
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


# Hook Definitions Transport
root_hooks.add(Transport.OutProfile.grain_size)  # To initialize calculation of the mean grain size


# Mean Temperature during Transport
def mean_temp_transport(self: Transport):
    """Mean temperature between beginning and end of transport"""
    return (self.in_profile.temperature + self.out_profile.temperature) / 2


# Hook Definitions Transport (MDRX)
Transport.half_recrystallization_time = Hook[float]()
"""Time needed for half the microstructure to metadynamically recrystallize"""

Transport.OutProfile.recrystallized_grain_size = Hook[float]()
"""Grain size of metadynamic recrystallized grains"""

Transport.zener_holomon_parameter = Hook[float]()
"""Zener-Holomon-Parameter of the transport"""

Transport.OutProfile.recrystallized_fraction = Hook[float]()
"""Fraction of microstructure which is recrystallized"""

Transport.recrystallization_mechanism = Hook[str]()


@Transport.recrystallization_mechanism
def transport_recrystallization_mechanism(self: Transport):
    if prev_roll_pass(self).out_profile.recrystallization_state == 'full':
        return "none"
    elif prev_roll_pass(self).out_profile.recrystallization_state == 'partial':
        return "metadynamic"
    else:
        return "static"


# Change in strain during transport
@Transport.OutProfile.strain
def transport_out_strain(self: Transport.OutProfile):
    if prev_roll_pass(self.transport).out_profile.recrystallization_state == 'full':
        self.logger.info("Material is fully recrystallized at the beginning of the transport")
        return 0
    return self.transport.in_profile.strain * (1 - self.recrystallized_fraction)


# Change in grain size during transport
@Transport.OutProfile.grain_size
def transport_out_grain_size(self: Transport.OutProfile):
    return transport_grain_growth(self.transport)


def transport_out_grain_size_metadynamic_without_growth(transport):
    """Mean grain size after metadynamic recrystallization"""
    rp = prev_roll_pass(transport)

    return (
            transport.in_profile.grain_size
            + ((transport.out_profile.recrystallized_grain_size - transport.in_profile.grain_size)
               * transport.out_profile.recrystallized_fraction)
    )


@Transport.OutProfile.recrystallized_fraction
def transport_out_recrystallized_fraction_metadynamic(self: Transport.OutProfile):
    """Fraction of microstructure which is recrystallized"""
    if self.transport.recrystallization_mechanism == "metadynamic":
        recrystallized = 1 - np.exp(
            np.log(0.5)
            * (self.transport.duration / self.transport.half_recrystallization_time)
            ** self.jmak_parameters.n_md
        )

        if np.isfinite(recrystallized):
            return recrystallized
        else:
            return 1


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


@Transport.OutProfile.recrystallized_grain_size
def transport_out_recrystallized_grain_size_metadynamic(self: Transport.OutProfile):
    """Mean grain size of metadynamically recrystallized grains"""
    if self.transport.recrystallization_mechanism == "metadynamic":
        return self.jmak_parameters.p11 * (self.transport.zener_holomon_parameter ** - self.jmak_parameters.p12)


@Transport.zener_holomon_parameter
def transport_zener_holomon_parameter(self: Transport):
    strain_rate = prev_roll_pass(self).strain_rate
    return (
            strain_rate
            * np.exp(self.in_profile.jmak_parameters.q_def / (Config.GAS_CONSTANT * mean_temp_transport(self)))
    )


def transport_out_grain_size_static_without_growth(transport):
    """Mean grain size after static recrystallization"""
    return (
            transport.out_profile.recrystallized_fraction ** (4 / 3)
            * transport.out_profile.recrystallized_grain_size
            + (1 - transport.out_profile.recrystallized_fraction) ** 2
            * transport.in_profile.grain_size
    )


@Transport.OutProfile.recrystallized_fraction
def transport_out_recrystallized_fraction_static(self: Transport.OutProfile):
    """Fraction of microstructure which is recrystallized"""
    if self.transport.recrystallization_mechanism == "static":
        recrystallized = 1 - np.exp(
            np.log(0.5)
            * (self.transport.duration / self.transport.half_recrystallization_time)
            ** self.jmak_parameters.n_s
        )

        if np.isfinite(recrystallized):
            return recrystallized
        else:
            return 1


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


@Transport.OutProfile.recrystallized_grain_size
def transport_out_recrystallized_grain_size_static(self: Transport.OutProfile):
    """Mean grain size of static recrystallized grains"""
    if self.transport.recrystallization_mechanism == "static":
        strain_rate = prev_roll_pass(self.transport).strain_rate
        return (
                self.jmak_parameters.b
                * self.transport.in_profile.strain ** (-self.jmak_parameters.b1)
                * strain_rate ** (-self.jmak_parameters.b2)
                * self.transport.in_profile.grain_size ** self.jmak_parameters.b3
                * np.exp(self.jmak_parameters.q_dsrx / (Config.GAS_CONSTANT * mean_temp_transport(self.transport)))
        )


def transport_grain_growth(self: Transport):
    if prev_roll_pass(self).out_profile.recrystallization_state == 'full':
        self.logger.info("Grain growth after dynamic recrystallization")
        d_rx = self.in_profile.grain_size
        duration_left = self.duration
    elif prev_roll_pass(self).out_profile.recrystallization_state == 'partial':
        self.logger.info("Grain growth after metadynamic recrystallization")
        d_rx = transport_out_grain_size_metadynamic_without_growth(self)
        duration_left = (
                self.duration
                - (np.log(self.in_profile.jmak_parameters.threshold) / np.log(0.5))
                ** (1 / self.in_profile.jmak_parameters.n_md)
                * self.half_recrystallization_time
        )
    else:
        self.logger.info("Grain growth after static recrystallization")
        d_rx = transport_out_grain_size_static_without_growth(self)
        duration_left = (
                self.duration
                - (np.log(self.in_profile.jmak_parameters.threshold) / np.log(0.5))
                ** (1 / self.in_profile.jmak_parameters.n_s)
                * self.half_recrystallization_time
        )

    if duration_left < 0:
        return d_rx

    return (
            (d_rx ** self.in_profile.jmak_parameters.s
             + self.in_profile.jmak_parameters.k * duration_left
             * np.exp(-self.in_profile.jmak_parameters.q_grth / (Config.GAS_CONSTANT * mean_temp_transport(self))))
            ** (1 / self.in_profile.jmak_parameters.s)
    )
