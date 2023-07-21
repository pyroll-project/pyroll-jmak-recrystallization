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
RollPass.recrystallisation_critical_strain = Hook[float]()
"""Critical strain needed for onset of dynamic recrystallization"""

RollPass.recrystallisation_steady_state_strain = Hook[float]()
"""Calculation of strain for steady state flow during dynamic recrystallization"""

RollPass.OutProfile.recrystallized_grain_size = Hook[float]()
"""Grain size of dynamic recrystallized grains"""

RollPass.zener_holomon_parameter = Hook[float]()
"""Zener-Holomon-Parameter"""

RollPass.OutProfile.recrystallisation_state = Hook[str]()
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
    recrystallized = 1 - np.exp(
        -self.jmak_parameters.p7
        * (
                (self.roll_pass.strain - self.roll_pass.recrystallisation_critical_strain)
                / (
                        self.roll_pass.recrystallisation_steady_state_strain - self.roll_pass.recrystallisation_critical_strain)
        ) ** self.jmak_parameters.p8)
    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 1


@RollPass.recrystallisation_critical_strain
def roll_pass_recrystallisation_critical_strain(self: RollPass):
    """Calculation of the critical strain needed for the onset of dynamic recrystallization"""
    p = self.in_profile

    return (
            p.jmak_parameters.c * p.jmak_parameters.p1
            * (p.roll_pass.in_profile.grain_size ** p.jmak_parameters.p2)
            * (p.roll_pass.zener_holomon_parameter ** p.jmak_parameters.p3)
    )


@RollPass.recrystallisation_steady_state_strain
def roll_pass_recrystallisation_steady_state_strain(self: RollPass):
    """Calculation of strain for steady state flow during dynamic recrystallization"""
    p = self.in_profile

    return (
            p.jmak_parameters.p4
            * (p.roll_pass.in_profile.grain_size ** p.jmak_parameters.p5)
            * (p.roll_pass.zener_holomon_parameter ** p.jmak_parameters.p6)
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
    return self.roll_pass.out_profile.recrystallized_grain_size


# pretty sure that there is a better way
@RollPass.OutProfile.recrystallisation_state
def roll_pass_out_recrystallisation_state(self: RollPass.OutProfile):
    """Function to determine if dynamic recrystallization happened or not
    if return = 'fully recrystallized' -> material is fully recrystallized
    if return = 'yes' -> dynamic recrystallization happened
    if return = 'no' -> dynamic recrystallization didn't happen
    """
    if self.roll_pass.out_profile.recrystallized_fraction > 1 - self.jmak_parameters.threshold:
        return "fully recrystallized"
    elif self.roll_pass.out_profile.recrystallized_fraction > self.jmak_parameters.threshold:
        return "yes"
    else:
        return "no"


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
Transport.half_recrystallisation_time_metadynamic = Hook[float]()
"""Time needed for half the microstructure to metadynamically recrystallize"""

Transport.OutProfile.recrystallized_grain_size_metadynamic = Hook[float]()
"""Grain size of metadynamic recrystallized grains"""

Transport.zener_holomon_parameter = Hook[float]()
"""Zener-Holomon-Parameter of the transport"""

Transport.OutProfile.recrystallized_fraction_metadynamic = Hook[float]()
"""Fraction of microstructure which is recrystallized"""


# Change in strain during transport
@Transport.OutProfile.strain
def transport_out_strain(self: Transport.OutProfile):
    if prev_roll_pass(self.transport).out_profile.recrystallisation_state == 'fully recrystallized':
        self.logger.info("Material is fully recrystallized at the beginning of the transport")
        return 0
    elif prev_roll_pass(self.transport).out_profile.recrystallisation_state == 'yes':
        self.logger.info("Metadynamic recrystallization happened")
        return transport_out_strain_metadynamic(self.transport)
    else:
        self.logger.info("Static recrystallization happened")
        return transport_out_strain_static(self.transport)


# Change in grain size during transport
@Transport.OutProfile.grain_size
def transport_out_grain_size(self: Transport.OutProfile):
    if prev_roll_pass(self.transport).out_profile.recrystallisation_state == "fully recrystallized":
        return self.transport.grain_growth
    elif prev_roll_pass(self.transport).out_profile.recrystallisation_state == "yes":
        self.logger.info("Calculation of mean grain size according to equations for metadynamic recrystallization")
        return transport_out_grain_size_metadynamic(self.transport)
    else:
        self.logger.info("Calculation of mean grain size according to equations for static recrystallization")
        return transport_out_grain_size_static(self.transport)


# Metadynamic Recrystallization
def transport_out_strain_metadynamic(transport):
    """Strain after metadynamic recrystallization"""
    return transport.in_profile.strain * (1 - transport.out_profile.recrystallized_fraction_metadynamic)


def transport_out_grain_size_metadynamic(transport):
    """Mean grain size after metadynamic recrystallization"""
    return (
            prev_roll_pass(transport).out_profile.recrystallized_grain_size
            + ((prev_roll_pass(
        transport).out_profile.recrystallized_grain_size - transport.out_profile.recrystallized_grain_size_metadynamic)
               * transport.out_profile.recrystallized_fraction_metadynamic)
    ) + transport.grain_growth


@Transport.OutProfile.recrystallized_fraction_metadynamic
def transport_out_recrystallized_fraction_metadynamic(self: Transport.OutProfile):
    """Fraction of microstructure which is recrystallized"""
    recrystallized = 1 - np.exp(
        -np.log(0.5)
        * (
                self.transport.duration / self.transport.half_recrystallisation_time_metadynamic
        ) ** self.jmak_parameters.n_md)

    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 1


@Transport.half_recrystallisation_time_metadynamic
def transport_half_recrystallisation_time_metadynamic(self: Transport):
    """Time needed for half the microstructure to metadynamically recrystallize"""
    p = self.in_profile

    return (
            p.jmak_parameters.a_md
            * (self.zener_holomon_parameter ** p.jmak_parameters.n_zm)
            * np.exp(p.jmak_parameters.q_md / (Config.GAS_CONSTANT * mean_temp_transport(self)))
    )


@Transport.OutProfile.recrystallized_grain_size_metadynamic
def transport_out_recrystallized_grain_size_metadynamic(self: Transport.OutProfile):
    """Mean grain size of metadynamically recrystallized grains"""
    return self.jmak_parameters.p11 * (self.transport.zener_holomon_parameter ** - self.jmak_parameters.p12)


@Transport.zener_holomon_parameter
def transport_zener_holomon_parameter(self: Transport):
    strain_rate = prev_roll_pass(self).strain_rate
    return (
            strain_rate
            * np.exp(self.in_profile.jmak_parameters.q_def / (Config.GAS_CONSTANT * mean_temp_transport(self)))
    )


# Hook Definitions Transport (SRX)
Transport.half_recrystallisation_time_static = Hook[float]()
"""Time needed for half the microstructure to statically recrystallize"""

Transport.OutProfile.recrystallized_grain_size_static = Hook[float]()
"""Mean grain size of the statically recrystallized grains"""

Transport.OutProfile.recrystallized_fraction_static = Hook[float]()
"""Fraction of microstructure which is recrystallized"""


# Static Recrystallization
def transport_out_strain_static(transport):
    """Strain after static recrystallization"""
    return transport.in_profile.strain * (1 - transport.out_profile.recrystallized_fraction_static)


def transport_out_grain_size_static(transport):
    """Mean grain size after static recrystallization"""
    return (
            (transport.out_profile.recrystallized_fraction_static ** (
                    4 / 3)) * transport.out_profile.recrystallized_grain_size_static
            + ((1 - transport.out_profile.recrystallized_fraction_static) ** 2) * transport.in_profile.grain_size
    ) + transport.grain_growth


@Transport.OutProfile.recrystallized_fraction_static
def transport_out_recrystallized_fraction_static(self: Transport.OutProfile):
    """Fraction of microstructure which is recrystallized"""
    recrystallized = 1 - np.exp(
        -np.log(0.5)
        * (
                self.transport.duration / self.transport.half_recrystallisation_time_static
        ) ** self.jmak_parameters.n_s)

    if np.isfinite(recrystallized):
        return recrystallized
    else:
        return 1


@Transport.half_recrystallisation_time_static
def transport_half_recrystallisation_time_static(self: Transport):
    """Time needed for 50% to recrystallize"""
    strain_rate = prev_roll_pass(self).strain_rate
    p = self.in_profile

    return (
            p.jmak_parameters.a
            * (p.strain ** (- p.jmak_parameters.a1))
            * (strain_rate ** p.jmak_parameters.a2)
            * (p.grain_size ** p.jmak_parameters.a3)
            * np.exp(
        p.jmak_parameters.q_srx / (Config.GAS_CONSTANT * mean_temp_transport(self))
    )
    )


@Transport.OutProfile.recrystallized_grain_size_static
def transport_out_recrystallized_grain_size_static(self: Transport.OutProfile):
    """Mean grain size of static recrystallized grains"""
    strain_rate = prev_roll_pass(self.transport).strain_rate
    return (
            self.jmak_parameters.b
            * (self.transport.in_profile.strain ** (- self.jmak_parameters.b1))
            * (strain_rate ** (- self.jmak_parameters.b2))
            * (self.transport.in_profile.grain_size ** self.jmak_parameters.b3)
            * np.exp(
        self.jmak_parameters.q_dsrx / (Config.GAS_CONSTANT * mean_temp_transport(self.transport))
    )
    )


# Hook Definitions Transport (Grain Growth)
Transport.grain_growth = Hook[float]()
"""Functions to calculate the grain growth depending on type of recrystallization happening beforehand"""


# Grain Growth
@Transport.grain_growth
def transport_grain_growth(self: Transport):
    """Function for grain growth

    - if: microstructure is completely recrystallized -> only grain growth
    - elif: dynamic recrystallization happened -> new starting point: metadynamic recrystallization
    - else: static recrystallization as starting point
    | d_rx: mean grain size after recrystallization
    | duration_left: time left for grain growth after full recrystallization
    """
    if prev_roll_pass(self).out_profile.recrystallisation_state == 'fully recrystallized':
        self.logger.info("Grain growth after dynamic recrystallization")
        d_rx = prev_roll_pass(self).out_profile.recrystallized_grain_size
        duration_left = self.duration
    elif prev_roll_pass(self).out_profile.recrystallisation_state == 'yes':
        self.logger.info("Grain growth after metadynamic recrystallization")
        d_rx = transport_out_grain_size_metadynamic(self)
        duration_left = (
                self.duration
                - ((np.log(self.in_profile.jmak_parameters.threshold) / np.log(0.5)) ** (
                1 / self.in_profile.jmak_parameters.n_md))
                * self.half_recrystallisation_time_metadynamic
        )
    else:
        self.logger.info("Grain growth after static recrystallization")
        d_rx = transport_out_grain_size_static(self)
        duration_left = (
                self.duration
                - ((
                           (np.log(self.in_profile.jmak_parameters.threshold) / np.log(0.5)) ** (
                           1 / self.in_profile.jmak_parameters.n_s)
                   ) * self.half_recrystallisation_time_static)
        )
    return (
            (
                    d_rx ** self.in_profile.jmak_parameters.s + self.in_profile.jmak_parameters.k * duration_left
                    * np.exp(- (self.in_profile.jmak_parameters.q_grth
                                / (Config.GAS_CONSTANT * mean_temp_transport(self))))
            ) ** (1 / self.in_profile.jmak_parameters.s)
    )
