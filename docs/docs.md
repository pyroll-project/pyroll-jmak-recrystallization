# The PyRolL JMAK Plugin

This plugin provides a set of JMAK-type microstructure evolution equations for static recrystallisation, dynamic
recrystallisation, metadynamic recrystallisation and grain growth. Four sample material data sets are included in the
plugin for C45, S355J2, 54SiCr6 and C20.

## Model Equations

## Usage

To use the sample datasets provided, it is sufficient to provide the respective key in `Profile.material`. For own
coefficient sets, give the `Profile.jmak_parameters` hook, whose value must be an instance of the `JMAKParameters` class
provided with this package. For example:

```python
in_profile = Profile.round(
    ...,
    jmak_parameters=JMAKParameters(
        q_def=258435.17,
        c=0.79,
        p1=1.2338e-3,
        p2=0.3007,
        p3=0.1971,
        p4=6.6839e-4,
        p5=0.4506,
        p6=0.2265,
        p7=1.4952,
        p8=1.7347,
        p9=1072.98,
        p10=0.1629,

        n_s=1.505,
        a=3.7704e-8,
        a1=1.1988,
        a2=-1.003,
        a3=0.1886,
        q_srx=163457.62,
        b=0.1953,
        b1=0.7016,
        b2=0.0101,
        b3=1.2052,
        q_dsrx=6841.34,

        n_md=2.038,
        a_md=6.9235e-2,
        q_md=248617.4,
        n_zm=-0.9245,

        p11=840.57,
        p12=0.1629,
        s=6.0,
        k=1.9144e8,
        q_grth=30000.0
    ),
    ...
)
```

Most remarkable hooks for the user defined by this plugin are the following:

| Host      | Name                        | Meaning                                                                                              | Range                             |
|-----------|-----------------------------|------------------------------------------------------------------------------------------------------|-----------------------------------|
| `Profile` | `recrystallized_fraction`   | portion of the microstructure that is considered as recrystallized (without deformation experienced) | 0 to 1                            |
| `Profile` | `recrystallization_state`   | verbal classification of the recrystallisation state                                                 | `"full"`, `"partial"` or `"none"` |
| `Unit`    | `recrystallized_fraction`   | portion of the microstructure that is recrystallized within this unit                                | 0 to 1                            |
| `Unit`    | `recrystallized_grain_size` | grain size of the newly created grains in this unit                                                  | positive float (meters)           |

The `strain` value of out profiles in each unit are lowered by the `recrystallized_fraction`. The `grain_size` hook is
calculated by the weighted mean of incoming grain size and `recrystallized_grain_size`.

## Implementation Notes

In roll passes, there is always the dynamic recrystallization mechanism in operation. The type of recrystallization
mechanism happening in a transport is selected by the value of the newly
introduced `Transport.recrystallization_mechanism` hook, which is determined as follows:

| Value           | Condition                                                                            | Mechanisms                                     |
|-----------------|--------------------------------------------------------------------------------------|------------------------------------------------|
| `"none"`        | if the `recrystallisation_state` of the in profile is `"full"`                       | only grain growth                              |
| `"metadynamic"` | if the `recrystallisation_state` of the in profile is `"partial"`                    | metadynamic recrystallization and grain growth |
| `"static"`      | otherwise, especially if the `recrystallisation_state` of the in profile is `"none"` | static recrystallization and grain growth      |

The value of the `Profile.recrystallisation_state` hook is determined as follows using a threshold value that is an
attribute of the `JMAKParameters` class:

| Value        | Condition                                                                       |
|--------------|---------------------------------------------------------------------------------|
| `"none"`     | if the `recrystallized_fraction"` of the profile is smaller than `threshold`    |
| `"full"`     | if the `recrystallized_fraction"` of the profile is larger than `1 - threshold` |
| `'"partial"` | otherwise                                                                       |

These string keys are selected in the other hook implementations to select there appropriateness for the current unit
and with that choosing the equation set to use. 

