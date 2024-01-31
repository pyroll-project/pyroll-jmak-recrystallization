# The PyRolL JMAK Plugin

This plugin provides a set of JMAK-type microstructure evolution equations for static recrystallisation, dynamic
recrystallisation, metadynamic recrystallisation and grain growth. Four sample material data sets are included in the
plugin for C45, S355J2, 54SiCr6 and C20.

## Model Equations

### Definitions

| Symbol    | Meaning                       |
|-----------|-------------------------------|
| $f$       | recrystallized fraction       |
| $d$       | mean grain size               |
| index $0$ | incoming/start value          |
| index $1$ | outgoing/end value            |
| $\varphi$ | equivalent strain             |
| $Z$       | Zener-Holomon-Parameter       |
| $T$       | temperature                   |
| $t$       | time                          |
| RX        | recrystallisation             |
| DRX       | dynamic recrystallisation     |
| SRX       | static recrystallisation      |
| MRX       | metadynamic recrystallisation |
| GG        | grain growth                  |


### Dynamic Recrystallization

$$
f_\mathrm{DRX} = 1 - \exp \left[ -p_7 \frac{\varphi_0 + \Delta\varphi - \varphi_\mathrm{c}}{\varphi_\mathrm{s} - \varphi_\mathrm{c}} \right]
$$

$$
\varphi_\mathrm{c} = c \cdot p_1 \cdot (d_0 \cdot 10^6)^{p_2} \cdot Z^{p_3}
$$

$$
\varphi_\mathrm{s} = p_4 \cdot p_1 \cdot (d_0 \cdot 10^6)^{p_5} \cdot Z^{p_6}
$$

$$
d_\mathrm{DRX} = p_9 Z^{-p_{10}} \cdot 10^{-6}
$$

$$
d_1 = d_0 + (d_\mathrm{DRX} - d_0) f_\mathrm{SRX}
$$

$$
Z = \dot\varphi \exp \left[-\frac{Q_\mathrm{def}}{RT}\right]
$$

### Metadynamic Recrystallization

The Zener-Holomon-Parameter of metadynamic recrystallization is equal to that of the deformation, where the recrystallization started. 

$$
f_\mathrm{MRX} = 1 - \exp \left[ \lg 0.5 \left( \frac{t}{t_{0.5}} \right)^{n_\mathrm{md}} \right]
$$

$$
t_{0.5} = a_\mathrm{md} \cdot Z^{n_\mathrm{zm}} \cdot \exp \left[ \frac{Q_\mathrm{md}}{RT} \right]
$$

$$
d_\mathrm{MRX} = p_{11} Z^{-p_{12}} \cdot 10^{-6}
$$

$$
d_1 = d_0 + (d_\mathrm{MRX} - d_0) f_\mathrm{SRX} 
$$

$$
f_1 = f_0 + (1 - f_0) f_\mathrm{MRX}
$$

### Static Recrystallization

$$
f_\mathrm{MRX} = 1 - \exp \left[ \lg 0.5 \left( \frac{t}{t_{0.5}} \right)^{n_\mathrm{s}} \right]
$$

$$
t_{0.5} = a \cdot \varphi_0^{a_1} \cdot \dot\varphi^{a_3} \cdot (d_0 \cdot 10^6)^{a_3} \cdot \exp \left[ \frac{Q_\mathrm{srx}}{RT} \right]
$$

$$
d_\mathrm{MRX} = b \cdot \varphi_0^{b_1} \cdot \dot\varphi^{b_3} \cdot (d_0 \cdot 10^6)^{b_3} \cdot \exp \left[ \frac{Q_\mathrm{dsrx}}{RT} \right] \cdot 10^{-6}
$$

$$
d_1 = (f_\mathrm{SRX})^{\frac{4}{3}} d_\mathrm{SRX} + (1 - f_\mathrm{SRX})^2 d_0
$$

$$
f_1 = f_0 + (1 - f_0) f_\mathrm{SRX}
$$

### Grain Growth

$$
d_1 = \left((d_0 \cdot 10^6)^{s} + k t \exp \left[ -\frac{Q_\mathrm{grth}}{RT} \right] \right)^{\frac{1}{s}}
$$

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

