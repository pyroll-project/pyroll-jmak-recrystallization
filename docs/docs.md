# The PyRolL JMAK-Recrystallization Plugin

This plugin provides a set of JMAK-type microstructure evolution equations for static recrystallization, dynamic
recrystallization, metadynamic recrystallization and grain growth under constant process conditions (time, temperature
strain , strain rate).  
Four sample material data sets are included in the plugin for C45, S355J2, 54SiCr6 and C20.

## Model Equations

The JMAK model was originally founded and named after Johnson and Mehl [^Johnson1939],
Avrami [^Avrami1939] [^Avrami1940] [^Avrami1941] and Kolmogorov [^Kolmogorov1937]. The following equations do not
represent the basic theory, but are adapted versions for the four recrystallization stages (dynamic, metadynamic,
static, grain growth) published elsewhere in literature (given at respective position). All of them need a set of
empirical parameters which characterize the behavior of a material with a certain chemical composition under defined
conditions. Note, that although the parameters are named equally for all mechanisms, they have distinct values for each
mechanism. A few sample sets of these parameters are included in the package, additional can be found in literature or
measured and determined by the user.

The following equations try to catch up as many of the various forms found in literature as possible, to be able to use
existing coefficient sets. They cannot be found in literature in these exact forms, but are a merge of existing ones.
Also, it was tried to name the parameters for the different mechanisms as coherent as possible. The use of the
Zener-Holomon-parameter [^ZenerHolomon1944] is avoided here, but individual Arrhenius-terms are introduced to allow
usage of distinct activation energies in each equation. The factors of $10^6$ are introduced with the grain sizes, since
commonly the grain size is given in $\mathrm{\mu m}$, but PyRolL uses $m$ as plain SI-unit everywhere and validity of
existing coefficient sets shall be maintained.

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
| RX                         | recrystallization                       |
| DRX                        | dynamic recrystallization               |
| SRX                        | static recrystallization                |
| MRX                        | metadynamic recrystallization           |
| GG                         | grain growth                            |

### Static Recrystallization

Static recrystallization is modelled scaled on a reference time as originally given by Sellars [^Sellars1979], with $t_
\mathrm{ref} = t_{0.5}$ as the time of half recrystallization. In the latter case, the factor $k = \ln \frac12$.The
strain rate and temperature dependence was introduced by Laasraoui [^Laasraoui1991], where the strain rate equals that
of the latest deformation step.

The statically recrystallized fraction is given as:

$$ X_\mathrm{SRX} = 1 - \exp \left[ k \left( \frac{t - t_\mathrm{c}}{t_\mathrm{ref} - t_\mathrm{c}} \right)^n \right]
$$

The critical time of the recrystallization start (incubation time) is given as (sometimes assumed as just zero):

$$ t_\mathrm{c} = a_1 \cdot \varphi_\mathrm{in}^{a_2} \cdot \dot\varphi^{a_3} \cdot (D_\mathrm{in} \cdot 10^6)^{a_4}
\cdot \exp \left[ -\frac{Q_a}{RT} \right]
$$

The reference time is given as below.

$$ t_\mathrm{ref} = b_1 \cdot \varphi_\mathrm{in}^{b_2} \cdot \dot\varphi^{b_3} \cdot (D_\mathrm{in} \cdot 10^6)^{b_4}
\cdot \exp \left[ -\frac{Q_b}{RT} \right]
$$

The mean diameter of freshly recrystallized grains is given as:

$$ D_\mathrm{SRX} = d_1 \cdot \varphi_\mathrm{in}^{d_2} \cdot \dot\varphi^{d_3} \cdot (D_\mathrm{in} \cdot 10^6)^{d_4}
\cdot \exp \left[ -\frac{Q_d}{RT} \right] \cdot 10^{-6} $$

The mean grain size at the output of the roll pass is given as:

$$ D_\mathrm{out} = (X_\mathrm{SRX})^{\frac{4}{3}} D_\mathrm{SRX} + (1 - X_\mathrm{SRX})^2 D_\mathrm{in} $$

The recrystallized at the output is given by a law of mixture as:

$$ X_\mathrm{out} = X_\mathrm{in} + (1 - X_\mathrm{in}) X_\mathrm{SRX} $$

### Dynamic Recrystallization

Dynamic recrystallization is modelled on natural log. strain $\varphi$ scale rather than time scale as originally given
by Karhausen [^Karhausen1992] based on the work of Roberts [^Roberts1979].

The dynamically recrystallized volume fraction of the microstructure is given as:

$$ X_\mathrm{DRX} = 1 - \exp
\left[ -k \left( \frac{\varphi - \varphi_\mathrm{c}}{\varphi_\mathrm{s} - \varphi_\mathrm{c}} \right) ^ n \right]
$$

The critical strain for the start of recrystallization is given as:

$$ \varphi_\mathrm{c} = a_1 \cdot \varphi_\mathrm{in}^{a_2} \cdot \dot\varphi^{a_3} \cdot (D_\mathrm{in} \cdot 10^6)^{a_4}
\cdot \exp \left[ -\frac{Q_a}{RT} \right]
$$

The reference strain is given as:

$$ \varphi_\mathrm{ref} = b_1 \cdot \varphi_\mathrm{in}^{b_2} \cdot \dot\varphi^{b_3} \cdot (D_\mathrm{in} \cdot 10^6)^{b_4}
\cdot \exp \left[ -\frac{Q_b}{RT} \right]
$$

The mean diameter of new recrystallized grains is given as:

$$ D_\mathrm{DRX} = d_1 \cdot Z^{d_2} \cdot 10^{-6} $$

The mean grain size at the output of the roll pass is given as:

$$ D_\mathrm{out} = D_\mathrm{in} + (D_\mathrm{DRX} - D_\mathrm{in}) X_\mathrm{DRX} $$

The recrystallized volume fraction at the end of deformation equals the dynamically recrystallized fraction:

$$ X_\mathrm{out} = X_\mathrm{DRX} $$

### Metadynamic Recrystallization

Metadynamic recrystallization occurs after a prior incomplete dynamic recrystallization during deformation replaces the
static mechanism in this case. The kinetics resemble the ones of static recrystallization, but the grain sizes those of
dynamic recrystallization. The equations shown here were originally given by Hodgson [^Hodgson1992]. The
Zener-Holomon-Parameter used in metadynamic recrystallization is equal to that of the prior deformation step (like with
strain rate in static recrystallization above).

The metadynamically recrystallized volume fraction of the microstructure is given as:

$$ X_\mathrm{MRX} = 1 - \exp \left[ \lg \frac{1}{2} \left( \frac{t}{t_{0.5}} \right)^n \right]
$$

The time for $50\% $ recrystallized volume fraction is given as:

$$ t_{0.5} = a_1 \cdot \varphi^{a_2} \cdot D_\mathrm{in}^{a_3} \cdot Z^{a_4} \cdot \exp \left[ -\frac{Q}{RT} \right]
$$

The mean diameter of new recrystallized grains is given as:

$$ D_\mathrm{MRX} = d_1 Z^{d_2} \cdot 10^{-6} $$

The mean grain size at the output of the roll pass is given as:

$$ D_\mathrm{out} = D_\mathrm{in} + (D_\mathrm{MRX} - D_\mathrm{in}) X_\mathrm{MRX} $$

The recrystallized at the output is given by a law of mixture as:

$$ X_\mathrm{out} = X_\mathrm{in} + (1 - X_\mathrm{in}) X_\mathrm{MRX} $$

### Grain Growth

Grain growth kinetics modelled as a root law rather than sigmoidal was originally given by Sellars [^Sellars1979] as:

$$ D_\mathrm{out} = \sqrt[d_1]{(D_\mathrm{in} \cdot 10^6)^{d_1} + d_2 t \exp \left[ -\frac{Q}{RT} \right] } $$

## Usage

To use the sample datasets provided, it is sufficient to provide the respective key in `Profile.material`. For own
coefficient sets, give the `Profile.jmak_parameters` hook, whose value must be an instance of the `JMAKParameters` class
provided with this package. A `JMAKParameters` object is itself composed
of `JMAKDynamicRecrystallizationParameters`, `JMAKStaticRecrystallizationParameters`, `JMAKMetadynamicRecrystallizationParameters`
and `JMAKGrainGrowthParameters` objects, which contain the parameters for the respective recrystallization mechanism.
Setting one of these to `None` disables the use of this mechanism. Especially missing parameters for metadynamic
recrystallization will cause a fallback to static recrystallization, even if the conditions for metadynamic where met.
For example:

```python
import pyroll.core as pr
import pyroll.jmak_recrystallization as prj

in_profile = pr.Profile.round(
    ...,
    jmak_parameters=prj.JMAKParameters(
        prj.JMAKDynamicRecrystallizationParameters(
            c=0.79,
            a1=1.2338e-3,
            a2=0.3007,
            a3=0.1971,
            b1=6.6839e-4,
            b2=0.4506,
            b3=0.2265,
            k=1.4952,
            n=1.7347,
            d1=1072.98,
            d2=-0.1629,
        ),
        prj.JMAKStaticRecrystallizationParameters(
            n=1.505,
            a1=3.7704e-8,
            a2=1.1988,
            a3=-1.003,
            a4=0.1886,
            qa=163457.62,
            d1=0.1953,
            d2=0.7016,
            d3=0.0101,
            d4=1.2052,
            qd=6841.34,
        ),
        prj.JMAKMetadynamicRecrystallizationParameters(
            n=2.038,
            a1=6.9235e-2,
            a2=0,
            a3=0,
            a4=-0.9245,
            qa=248617.4,
            d1=840.57,
            d2=-0.1629,
        ),
        prj.JMAKGrainGrowthParameters(
            d1=6.0,
            d2=1.9144e8,
            qd=30000.0
        )
    ),
    ...
)
```

Most remarkable hooks for the user defined by this plugin are the following:

| Host      | Name                        | Meaning                                                                                              | Range                             |
|-----------|-----------------------------|------------------------------------------------------------------------------------------------------|-----------------------------------|
| `Profile` | `recrystallized_fraction`   | portion of the microstructure that is considered as recrystallized (without deformation experienced) | 0 to 1                            |
| `Profile` | `recrystallization_state`   | verbal classification of the recrystallization state                                                 | `"full"`, `"partial"` or `"none"` |
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
| `"none"`        | if the `recrystallization_state` of the in profile is `"full"`                       | only grain growth                              |
| `"metadynamic"` | if the `recrystallization_state` of the in profile is `"partial"`                    | metadynamic recrystallization and grain growth |
| `"static"`      | otherwise, especially if the `recrystallization_state` of the in profile is `"none"` | static recrystallization and grain growth      |

The value of the `Profile.recrystallization_state` hook is determined as follows using a threshold value that is an
attribute of the `JMAKParameters` class:

| Value       | Condition                                                                       |
|-------------|---------------------------------------------------------------------------------|
| `"none"`    | if the `recrystallized_fraction"` of the profile is smaller than `threshold`    |
| `"full"`    | if the `recrystallized_fraction"` of the profile is larger than `1 - threshold` |
| `"partial"` | otherwise                                                                       |

These string keys are selected in the other hook implementations to select there appropriateness for the current unit
and with that choosing the equation set to use.

[^Karhausen1992]: K. Karhausen and R. Kopp, “Model for integrated process and microstructure simulation in hot forming,”
Steel Research, vol. 63, no. 6, pp. 247–256, Jun. 1992, doi: 10.1002/srin.199200509.
[^Roberts1979]: W. Roberts, H. Boden, and B. Ahlblom, “Dynamic recrystallization kinetics,” Metal Science, vol. 13, no.
3–4, pp. 195–205, Mar. 1979, doi: 10.1179/msc.1979.13.3-4.195.
[^Hodgson1992]: P. D. Hodgson and R. K. Gibbs, “A Mathematical Model to Predict the Mechanical Properties of Hot Rolled
C-Mn and Microalloyed Steels.,” ISIJ International, vol. 32, no. 12, pp. 1329–1338, 1992, doi:
10.2355/isijinternational.32.1329.
[^Maccagno1996]: T. M. Maccagno, J. J. Jonas, and P. D. Hodgson, “Spreadsheet Modelling of Grain Size Evolution during
Rod Rolling.,” ISIJ International, vol. 36, no. 6, pp. 720–728, 1996, doi: 10.2355/isijinternational.36.720.
[^Johnson1939]: W. A. Johnson and R. F. Mehl, “Reaction Kinetics in Processes of Nucleation and Growth,” Trans. Am.
Inst. Min. Metall. Eng., vol. 135, pp. 416–458, 1939.
[^Avrami1939]: M. Avrami, “Kinetics of Phase Change. I General Theory,” The Journal of Chemical Physics, vol. 7, no. 12,
pp. 1103–1112, Dec. 1939, doi: 10.1063/1.1750380.
[^Avrami1940]: M. Avrami, “Kinetics of Phase Change. II Transformation-Time Relations for Random Distribution of
Nuclei,” The Journal of Chemical Physics, vol. 8, no. 2, pp. 212–224, Feb. 1940, doi: 10.1063/1.1750631.
[^Avrami1941]: M. Avrami, “Granulation, Phase Change, and Microstructure Kinetics of Phase Change. III,” The Journal of
Chemical Physics, vol. 9, no. 2, pp. 177–184, Feb. 1941, doi: 10.1063/1.1750872.
[^Kolmogorov1937]: A. Kolmogorov, “К статистической теории кристаллизации металлов,” Известия академии наук СССР, vol.
1, no. 3, pp. 355–359, 1937.
[^Laasraoui1991]: A. Laasraoui and J. J. Jonas, “Recrystallization of austenite after deformation at high temperatures
and strain rates—Analysis and modeling,” Metall Trans A, vol. 22, no. 1, pp. 151–160, Jan. 1991, doi:
10.1007/BF03350957.
[^Sellars1979]: C. M. Sellars and J. A. Whiteman, “Recrystallization and grain growth in hot rolling,” Metal Science,
vol. 13, no. 3–4, pp. 187–194, Mar. 1979, doi: 10.1179/msc.1979.13.3-4.187.
[^ZenerHolomon1944]: C. Zener and H. C. Holomon, "Effect of Strain Rate Upon Plastic Flow of Steel", Journal of Applied
Physics, vol. 15, no.1, pp. 22-32, Jan. 1944, doi: 10.1063/1.1707363

 