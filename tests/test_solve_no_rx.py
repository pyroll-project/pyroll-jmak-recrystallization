import logging
from pathlib import Path

import numpy as np
from pyroll.core import Profile, PassSequence, RollPass, Roll, CircularOvalGroove, Transport, RoundGroove


def test_solve(tmp_path: Path, caplog):
    caplog.set_level(logging.DEBUG, logger="pyroll")

    import pyroll.jmak

    in_profile = Profile.round(
        diameter=30e-3,
        temperature=1200 + 273.15,
        strain=0,
        material=["S235", "steel"],
        flow_stress=100e6,
        density=7.5e3,
        thermal_capacity=690,
        jmak_parameters=pyroll.jmak.JMAKParameters(
            p7=1,
            p8=1.2906,
            eps_crit=0.6,
            eps_s=0.7,
        ),
    )

    sequence = PassSequence([
        RollPass(
            label="Oval I",
            roll=Roll(
                groove=CircularOvalGroove(
                    depth=8e-3,
                    r1=6e-3,
                    r2=40e-3
                ),
                nominal_radius=160e-3,
                rotational_frequency=1
            ),
            gap=2e-3,
        ),
        Transport(
            label="I => II",
            duration=1
        ),
        RollPass(
            label="Round II",
            roll=Roll(
                groove=RoundGroove(
                    r1=1e-3,
                    r2=12.5e-3,
                    depth=11.5e-3
                ),
                nominal_radius=160e-3,
                rotational_frequency=1
            ),
            gap=2e-3,
        ),
    ])

    try:
        sequence.solve(in_profile)
    finally:
        print("\nLog:")
        print(caplog.text)

    assert np.isclose((in_profile.strain + sequence[0].strain), sequence[0].out_profile.strain)
