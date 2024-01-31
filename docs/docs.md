# The PyRolL JMAK Plugin

This plugin provides a set of JMAK-type microstructure evolution equations for static recrystallisation, dynamic
recrystallisation, metadynamic recrystallisation and grain growth. Four sample material data sets are included in the
plugin for C45, S355J2, 54SiCr6 and C20.

## Model Equations

The JMAK model was originally founded and named after Johnson and Mehl [^Johnson1939], Avrami [^Avrami1939] [^Avrami1940] [^Avrami1941] and Kolmogorov [^Kolmogorov1937].
The following equations do not represent the basic theory, but are adapted versions for the four recrystallisation stages (dynamic, metadynamic, static, grain growth) published elsewhere  in literature (given at respective position).
All of them need a set of empirical parameters which characterize the behavior of a material with a certain chemical composition under defined conditions.
Note, that  although the parameters are named equally for all mechanisms, they have distinct values for each mechanism.
A few sample sets of these parameters are included in the package, additional can be found in literature or measured and determined by the user.

### Definitions

The following table defines the mathematical symbols used in the equations.

| Symbol                     | Meaning                                 |
|----------------------------|-----------------------------------------|
| $X$                        | recrystallized fraction                 |
| $D$                        | mean grain size                         |
| index $\mathrm{in}$        | incoming/start value                    |
| index $\mathrm{out}$       | outgoing/end value                      |
| $\varphi$                  | equivalent strain                       |
| $a_i$, $b_i$, $c_i$, $d_i$ | material dependent empirical parameters |
| $Q_i$                      | activation energy                       |
| $Z$                        | Zener-Holomon-Parameter                 |
| $T$                        | temperature                             |
| $t$                        | time                                    |
| RX                         | recrystallisation                       |
| DRX                        | dynamic recrystallisation               |
| SRX                        | static recrystallisation                |
| MRX                        | metadynamic recrystallisation           |
| GG                         | grain growth                            |


### Static Recrystallization

Static recrystallisation is modelled scaled on the time of half recrystallisation as originally given by Sellars [^Sellars1979].

The statically recrystallized fraction is given as:

$$
X_\mathrm{MRX} = 1 - \exp \left[ \lg \frac{1}{2} \left( \frac{t}{t_{0.5}} \right)^n \right]
$$

The time of half recrystallisation is given as below. The strain rate dependence was introduced by Laasraoui [^Laasraoui1991], where the strain rate equals that of the latest deformation step.

$$
t_{0.5} = a_1 \cdot \varphi_\mathrm{in}^{a_2} \cdot \dot\varphi^{a_3} \cdot (D_\mathrm{in} \cdot 10^6)^{a_4} \cdot \exp \left[ -\frac{Q_a}{RT} \right]
$$

The mean diameter of freshly recrystallized grains is given as:

$$
D_\mathrm{SRX} = d_1 \cdot \varphi_\mathrm{in}^{d_2} \cdot \dot\varphi^{d_3} \cdot (D_\mathrm{in} \cdot 10^6)^{d_4} \cdot \exp \left[ -\frac{Q_d}{RT} \right] \cdot 10^{-6}
$$

The mean grain size at the output of the roll pass is given as:

$$
D_\mathrm{out} = (X_\mathrm{SRX})^{\frac{4}{3}} D_\mathrm{SRX} + (1 - X_\mathrm{SRX})^2 D_\mathrm{in}
$$

The recrystallized at the output is given by a law of mixture as:

$$
X_\mathrm{out} = X_\mathrm{in} + (1 - X_\mathrm{in}) X_\mathrm{SRX}
$$


### Dynamic Recrystallization


Dynamic recrystallisation is modelled on strain scale rather than time scale as originally given by Karhausen [^Karhausen1992] based on the work of Roberts [^Roberts1979].

The dynamically recrystallized fraction of the microstructure is given as:

$$
X_\mathrm{DRX} = 1 - \exp \left[ -k \left( \frac{\varphi_0 + \Delta\varphi - \varphi_\mathrm{c}}{\varphi_\mathrm{s} - \varphi_\mathrm{c}} \right) ^ n \right]
$$

The strain of maximum strength is given as:

$$
\varphi_\mathrm{m} = a_1 \cdot (D_\mathrm{in} \cdot 10^6)^{a_2} \cdot Z^{a_3}
$$

The steady state strain is given as:

$$
\varphi_\mathrm{s} = b_1 \cdot (D_\mathrm{in} \cdot 10^6)^{b_2} \cdot Z^{b_3}
$$

The critical strain for the start of recrystallisation is given as:

$$
\varphi_\mathrm{c} = c \cdot \varphi_\mathrm{m}
$$

The mean diameter of freshly recrystallized grains is given as:

$$
D_\mathrm{DRX} = d_1 \cdot Z^{d_2} \cdot 10^{-6}
$$

The mean grain size at the output of the roll pass is given as:

$$
D_\mathrm{out} = D_\mathrm{in} + (D_\mathrm{DRX} - D_\mathrm{in}) X_\mathrm{DRX}
$$

The recrystallized at the output equals the dynamically recrystallized fraction:

$$
X_\mathrm{out} = X_\mathrm{DRX}
$$

### Metadynamic Recrystallization

Metadynamic occurs after dynamic recrystallisation has happened before and replaces the static mechanism in this case.
The kinetics resemble the ones of static recrystallisation, but the grain sizes those of dynamic recrystallisation.
The equations shown here were originally given by Hodgson [^Hodgson1992].
The Zener-Holomon-Parameter used in metadynamic recrystallisation is equal to that of the latest deformation step (like with strain rate in static recrystallisation above. 

The metadynamically recrystallized fraction of the microstructure is given as:

$$
X_\mathrm{MRX} = 1 - \exp \left[ \lg \frac{1}{2} \left( \frac{t}{t_{0.5}} \right)^n \right]
$$

The time of half recrystallisation is given as:

$$
t_{0.5} = a_1 \cdot \varphi^{a_2} \cdot D_\mathrm{in}^{a_3} \cdot Z^{a_4} \cdot \exp \left[ -\frac{Q}{RT} \right]
$$

The mean diameter of freshly recrystallized grains is given as:

$$
D_\mathrm{MRX} = d_1 Z^{d_2} \cdot 10^{-6}
$$

The mean grain size at the output of the roll pass is given as:

$$
D_\mathrm{out} = D_\mathrm{in} + (D_\mathrm{MRX} - D_\mathrm{in}) X_\mathrm{MRX} 
$$

The recrystallized at the output is given by a law of mixture as:

$$
X_\mathrm{out} = X_\mathrm{in} + (1 - X_\mathrm{in}) X_\mathrm{MRX}
$$

### Grain Growth

Grain growth kinetics modelled as a root law rather than JMAK was originally given by Sellars [^Sellars1979] as:

$$
D_\mathrm{out} = \sqrt[d_1]{(D_\mathrm{in} \cdot 10^6)^{d_1} + d_2 t \exp \left[ -\frac{Q}{RT} \right] }
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

[^Karhausen1992]: K. Karhausen and R. Kopp, “Model for integrated process and microstructure simulation in hot forming,” Steel Research, vol. 63, no. 6, pp. 247–256, Jun. 1992, doi: 10.1002/srin.199200509.
[^Roberts1979]: W. Roberts, H. Boden, and B. Ahlblom, “Dynamic recrystallization kinetics,” Metal Science, vol. 13, no. 3–4, pp. 195–205, Mar. 1979, doi: 10.1179/msc.1979.13.3-4.195.
[^Hodgson1992]: P. D. Hodgson and R. K. Gibbs, “A Mathematical Model to Predict the Mechanical Properties of Hot Rolled C-Mn and Microalloyed Steels.,” ISIJ International, vol. 32, no. 12, pp. 1329–1338, 1992, doi: 10.2355/isijinternational.32.1329.
[^Maccagno1996]: T. M. Maccagno, J. J. Jonas, and P. D. Hodgson, “Spreadsheet Modelling of Grain Size Evolution during Rod Rolling.,” ISIJ International, vol. 36, no. 6, pp. 720–728, 1996, doi: 10.2355/isijinternational.36.720.
[^Johnson1939]: W. A. Johnson and R. F. Mehl, “Reaction Kinetics in Processes of Nucleation and Growth,” Trans. Am. Inst. Min. Metall. Eng., vol. 135, pp. 416–458, 1939.
[^Avrami1939]: M. Avrami, “Kinetics of Phase Change. I General Theory,” The Journal of Chemical Physics, vol. 7, no. 12, pp. 1103–1112, Dec. 1939, doi: 10.1063/1.1750380.
[^Avrami1940]: M. Avrami, “Kinetics of Phase Change. II Transformation-Time Relations for Random Distribution of Nuclei,” The Journal of Chemical Physics, vol. 8, no. 2, pp. 212–224, Feb. 1940, doi: 10.1063/1.1750631.
[^Avrami1941]: M. Avrami, “Granulation, Phase Change, and Microstructure Kinetics of Phase Change. III,” The Journal of Chemical Physics, vol. 9, no. 2, pp. 177–184, Feb. 1941, doi: 10.1063/1.1750872.
[^Kolmogorov1937]: A. Kolmogorov, “К статистической теории кристаллизации металлов,” Известия академии наук СССР, vol. 1, no. 3, pp. 355–359, 1937.
[^Laasraoui1991]: A. Laasraoui and J. J. Jonas, “Recrystallization of austenite after deformation at high temperatures and strain rates—Analysis and modeling,” Metall Trans A, vol. 22, no. 1, pp. 151–160, Jan. 1991, doi: 10.1007/BF03350957.
[^Sellars1979]: C. M. Sellars and J. A. Whiteman, “Recrystallization and grain growth in hot rolling,” Metal Science, vol. 13, no. 3–4, pp. 187–194, Mar. 1979, doi: 10.1179/msc.1979.13.3-4.187.


 