import logging
import webbrowser
from pathlib import Path

import pytest
from pyroll.core import (
    Profile,
    PassSequence,
    ThreeRollPass,
    Roll,
    CircularOvalGroove,
    Transport,
    RoundGroove,
)


@pytest.mark.parametrize(
    "material_id", ["S355J2", "C20", "C54SICE6", "C45", "C-Mn", "CuZn30"]
)
def test_solve(tmp_path: Path, caplog, material_id):
    caplog.set_level(logging.INFO, logger="pyroll")

    import pyroll.jmak_recrystallization

    in_profile = Profile.round(
        diameter=55e-3,
        temperature=1200 + 273.15,
        strain=0,
        material=[material_id, "steel"],
        flow_stress=100e6,
        density=7.5e3,
        thermal_capacity=690,
        grain_size=50e-6,
        recrystallized_fraction=0,
    )

    sequence = PassSequence([
        ThreeRollPass(
            label="Oval I",
            roll=Roll(
                groove=CircularOvalGroove(
                    depth=8e-3,
                    r1=6e-3,
                    r2=40e-3,
                    pad_angle=30
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
        ThreeRollPass(
            label="Round II",
            roll=Roll(
                groove=RoundGroove(
                    r1=3e-3,
                    r2=25e-3,
                    depth=11e-3,
                    pad_angle=30
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

    import pyroll.report

    f = tmp_path / "report.html"
    f.write_text(
        pyroll.report.report(sequence), encoding="utf-8"
    )  # encoding needed, don't know why
    print(f)

    webbrowser.open(f.as_uri())

    assert 0 < 1
