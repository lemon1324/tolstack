# tolstack

*This readme was last updated for application version 0.7.4.*

# Introduction

`tolstack` is designed to assist with tolerance analysis for engineering design. It is more than a 1D tool, as it implements functions beyond addition and subtraction, but does not support direct analysis of geometric dimensioning and tolerancing.

# Features

- Allows definition of dimensions with uniform or normal distributions.
- Associates part numbers and comments to dimensions for traceability.
- Implements addition, subtraction, multiplication, division, and exponentiation.
- Expression parser also handles parentheses and unary negation.
- Expressions can be evaluated in either worst-case or statistical modes against lower and/or upper bounds.
- Supports sensitivity analysis for nominal values, and contribution analysis for tolerances.
- Allows output to PDF and automatically includes images visually showing dimensions on parts and expressions.

# Using the Application

## Interface Layout
The left side of the user interface has three tabs:
- **Analysis Information**, which allows definition of metadata. All values are optional, but title and revision are strongly recommended. The description can be multiline Unicode text to provide a full description of the analysis being conducted.
- **Data**, which defines the actual numerical and expression values used for the analysis.
- **Options**, which sets various options controlling analysis outputs.

The right side contains an output window, which will contain a plain-text version of the analysis output for evaluating the output while iterating design values.
Three common options are also located here controlling various output evaluations useful for designing. See the [options](#options) section for more details.

## Workflow
The general workflow is as follows:

1. Define any constants for the problem. Constants have the following properties:
   - **Name:** The name used to refer to this constant in expressions.
   - **Value:** The value of the constant.
   - **Note:** Arbitrary Unicode text for documentation.
2. Define dimensions for the problem. These are the toleranced values for the problem (and may not actually be a 'dimension', just a number that has a tolerance). Dimensions have the following properties:

   - **Name:** The name used to refer to this dimension in expressions.
   - **Nominal:** The nominal value of the dimension. Will be used in calculating the nominal value of expressions.
   - **Plus:** The plus tolerance such that `nominal+plus` is the upper bound of this dimension. May be negative for unilateral bias tolerancing.
   - **Minus:** The minus tolerance such that `nominal+minus` is the lower bound of this dimension. May be positive for unilateral bias tolerancing. **Note the sign convention.** Minus tolerances for a bilaterally toleranced value should have a '-' sign in this field.
   - **D:** Distribution of this dimension. Default is uniform; other options are:
     - **U:** uniform distribution between `nominal+minus` and `nominal+plus`.
     - **1S, 2S, 3S:** normal distribution such that `μ=nominal+(plus+minus)/2`&mdash;that is, the mean is the midpoint between the extremes, _not_ the nominal value. The standard deviation is set such that `σ = (plus-minus)/2k` where `k={1,2,3}`. Note that the distribution code is the number of one-sided standard deviations.
   - **PN:** The part number this dimension is associated to. Should be no more than 9 characters.
   - **Note:** Arbitrary Unicode text for documentation.

   Dimensions must be defined such that `plus` is greater or equal to `minus`. Both tolerance values may also be expressed as percentages of the nominal value.

3. Define expressions to evaluate. Expressions have the following properties:
   - **Name:** The name used to refer to this expression. Can be referenced in other expressions, but only in a strictly sequential order.
   - **Value:** an infix expression using names of constants, dimensions, and already-defined expressions to define a mathematical quantity. May also include bare numeric values. An example would be `(D1+E2)/D3 + 5.2` Assuming `E2` has already been defined. Also supports the functions listed in [supported functions](#supported-functions).
   - **Lower:** The lower bound that this expression must satisfy to meet requirements. Will be flagged as a failed condition in the output if not met. Leave the cell empty to not set a lower bound.
   - **Upper:** The upper bound that this expression must satisfy to meet requirements. Will be flagged as a failed condition in the output if not met. Leave the cell empty to not set an upper bound.
   - **M:** the method by which to evaluate the expression. Default is worst-case; other options are:
     - **W:** worst-case evaluation; the nominal value will be propagated, and each operation will be evaluated in a worst-case sense. The output tolerance will be reported as plus/minus values from the nominal output value.
     - **1S, 2S, 3S:** statistical evaluation at ±1σ, ±2σ, and ±3σ. Each dimension is sampled several times from a distribution as defined in the dimension definition, and then the random samples have each operation applied element wise to simulate the final output in a Monte Carlo sense. The output is reported as the median value, with the -nσ and +nσ values defined by quantiles on the distribution such that the tails are equally weighted and have the same total weight as the tails in a normal distribution beyond ±nσ.
   - **Note:** Arbitrary Unicode text for documentation.

4. Run the analysis, and review results in the right-hand text pane. Enable/disable analysis options as required to proceed with the design process.

5. Optionally, create images to help illustrate dimension and expression definitions. See the [options](#options) section for details.

6. Export the analysis to text or PDF.

## Options
The three common options are:
- **Where Used:** if enabled, prints a 'where used' for each dimension in the dimension summary table. For example, if an expression E1 is defined as "2*D1", then the entry for D1 would read "Used in: E1, ...". Note that this is fully resolved, and so will indicate all expressions that are affected by this dimension, even if not directly referenced. For example, the combination of E1 defined as before along with E2 defined as "E1 + D2" will mean that D1 is used in E1 and E2, while D2 only in E2.
- **Sensitivity:** if enabled, for each expression prints a sensitivity analysis, where for each dimension used in that expression, the partial derivative with respect to that dimension is evaluated and printed.
- **Tolerance Contribution:** Will print an estimate of how much each dimension contributes to the overall tolerance of the expression. Computed by looping though all dimensions that an expression depends on, recomputing the expression with that dimension set to have zero tolerance, and evaluating the reduction in total tolerance range of the expression. Can be used to determine which dimensions are most important to refine to meet a particular bound.

The options in the options tab are:
- **Include images:** After the summary section, will go through all part numbers in the dimensions table, and for each part number `PN`, search for images of the form `PN.ext` and `PNx.ext`. Currently supported extensions are jpg, jpeg, png, gif, bmp, and tiff. If multiple images are required, the `PNx.ext` format can be used with alphanumeric sequence marks, e.g. PNa.png, PNb.png, etc. The images and dimensions associated to each part number will be printed next to each other in the PDF report, for ease of review. This will also search for images of the form `KEY.ext` for each key in the expression table, and will include that image alongside the evaluation of that expression.
- **Show distribution plots:** When enabled, this will include plots of the underlying distribution, computed limits, and defined bounds for each expression in PDF reports.
- **Units:** while not used for computation, this defines metadata text indicating the units used in this analysis, for convenience and clarity of documentation.
- **Image search folder:** Defines the location to search for images to include in PDF reports. If input as text, this should be a relative path from the location of the save file. If browsed to, the relative path will be automatically generated, but can only be performed once a file is either opened or saved.


## Supported Functions

In addition to the normal +, -, \*, /, `tolstack` also supports exponentiation (e.g. x^y) and unary negation (e.g. '-x'). The following functions are also supported:

- `sin(x)`, `cos(x)`, and `tan(x)`, which implement the trigonometric functions assuming the input quantity is in radians. Note that these are internally treated as unary operator tokens with high precedence, so for example 'sin -x' without explicit parentheses will evaluate to the sine of negative x.
- `sind(x)`, `cosd(x)`, and `tand(x)`, which are convenience functions to accept degree inputs. All the same notes apply as above.

## Menu Options
The top menu allows for file management, management of input data, and access to help and about information.

Note that the "Save" and "Save As" actions will always save the analysis definition file to disk. To save the outputs, "Export" should be used with either text output, which will save the contents of the right pane, or PDF output, which will render a PDF with images included if enabled.

Rename item will allow renaming a constant or dimension to a new name, and will update expressions referencing that item. Note that while this will warn on a name conflict, there is currently no undo functionality so be careful.

Sorting is also provided to ease table organization.  Note that since expressions cannot have backwards references, sorting is only available on the constants and dimensions tables.

# FAQ

- **How do I analyze geometric tolerances?**

  As geometric tolerances generally require full knowledge of the geometry to analyze, they are not currently set up to be natively analyzed in `tolstack`.

  However, as `tolstack` implements mathematical operations beyond addition, many geometric tolerances can be analyzed by decomposing them to equivalent +/- tolerances and composing them.

  For example, suppose we have a street sign of height H = 90±5% inches, with a mounting flange of diameter D = 6±0.25 in. Let's say the flange has a perpendicularity to the pole of 0.1 in. To determine how much the top of the pole can shift laterally, we can define an equivalent +/- tolerance T and multiply by H/D to get the motion of the top of the pole.

  Note that since the perpendicularity tolerance allows either the left side or the right side to be raised by .1" with respect to the other, the equivalent tolerance used in this example should be ±0.1 in.

  See the [street_sign.txt](examples/street_sign.txt) input file in the examples folder for the worked example file.

- **How do I analyze thermal variation?**

  `tolstack` is based around +/- tolerancing of basic numbers, and therefore the temperature needs to be converted to a multiplicative factor. The recommended usage is to define the material CTE(s) as constants C, temperature operating points T as dimensions with tolerance, and scale factors as expressions S = 1 + T\*C.

  As thermal variation depends both on the absolute temperature from the inspection temperature (for relative CTE tolerancing) and on the relative temperature between parts (for temperature-driven tolerancing), it may require multiple separate analysis rows to fully analyze thermal constraints. Here are a few examples, all assuming a pin of diameter D1 and a hole of diameter D2:

  - **Fit across wide operating range:** if the parts have the same temperature with a large common-mode variation, conduct two analyses, one at each temperature extreme. For each temperature, define a (constant) scale factor for each part S = 1 + T\*C at that temperature, and then evaluate the fit D2\*S2 - D1\*S1.

  - **Fit with arbitrary temperature difference:** If the parts have the same CTE but the temperature difference is unknown, define a single temperature with zero nominal value and symmetric uncertainty. Multiply both values by the common scale factor: D2\*S - D1\*S.

- **What does ±3σ actually mean?**

  For dimension inputs, this is the normal definition of standard deviation: the underlying distribution for that dimension will be normal, with a mean and standard distribution such that ±3σ matches the range from the minus tolerance to the plus tolerance. Note that the current implementation will always use a distribution that is symmetric about the limits, not about the provided nominal value, which will only be used to track what the "nominal" values of expressions are.

  For expressions, since the underlying distribution may not be normal in several cases, the end points are defined as quantiles of the output distribution. The quantiles are defined to have equal weight in the tails, and to have 99.7% between the tails, just as for a normal distribution at ±3σ.
