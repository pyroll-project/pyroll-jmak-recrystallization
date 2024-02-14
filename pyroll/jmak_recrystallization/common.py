import numpy as np

from .material_data import JMAKRecrystallizationParameters
from pyroll.core import Unit, Config


def average_temperature(unit: Unit):
    """Mean temperature between beginning and end of transport"""
    return (unit.in_profile.temperature + unit.out_profile.temperature) / 2


def critical_value_function(unit: Unit, strain_rate: float):
    p = unit.in_profile
    parameters = unit.jmak_recrystallization_parameters

    return (
        parameters.a1
        * p.strain**parameters.a2
        * strain_rate**parameters.a3
        * (p.grain_size * 1e6) ** parameters.a4
        * np.exp(
            parameters.qa / (Config.UNIVERSAL_GAS_CONSTANT * average_temperature(unit))
        )
    )


def reference_value_function(unit: Unit, strain_rate: float):
    p = unit.in_profile
    parameters = unit.jmak_recrystallization_parameters

    return (
        parameters.b1
        * p.strain**parameters.b2
        * strain_rate**parameters.b3
        * (p.grain_size * 1e6) ** parameters.b4
        * np.exp(
            parameters.qb / (Config.UNIVERSAL_GAS_CONSTANT * average_temperature(unit))
        )
    )
