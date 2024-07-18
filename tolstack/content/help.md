## About

`tolstack` is designed to assist with tolerance analysis for engineering design.

## Quick Reference

All numeric input fields support any string that can be parsed to a floating point value, including scientific notation. Inclusion or omission of: `+` signs; leading or trailing zeroes; and leading or trailing whitespace is also accepted.

**Name** fields should be 4 characters or fewer, and the recommended format is `Ann` where `A` is a letter and `nn` is a numeral, e.g. `C1`.

### Constants

- **Name:** The name used to refer to this constant in expressions.
- **Value:** The value of the constant.
- **Note:** Arbitrary unicode text for documentation.

### Dimensions

- **Name:** The name used to refer to this dimension in expressions.
- **Nominal:** The nominal value of the dimension. Will be used in calculating the nominal value of expressions.
- **Plus:** The plus tolerance such that `nominal+plus` is the upper bound of this dimension. May be negative for unilateral bias tolerancing.
- **Minus:** The minus tolerance such that `nominal+minus` is the lower bound of this dimension. May be positive for unilateral bias tolerancing. **Note the sign convention.**
- **D:** Distribution of this dimension. Default is uniform; other options are:
    - **U:** uniform distribution between `nominal+minus` and `nominal+plus`.
    - **1S, 2S, 3S:** normal distribution such that `μ=nominal+(plus+minus)/2`&mdash;that is, the mean is the midpoint between the extremes, _not_ the nominal value. The standard deviation is set such that `σ = (plus-minus)/2k` where `k={1,2,3}`. Note that the distribution code is the number of one-sided standard distributions.
- **PN:** The part number this dimension is associated to. Should be no more than 9 characters.
- **Note:** Arbitrary unicode text for documentation.

### Expressions

- **Name:** The name used to refer to this expression. Can be referenced in other expressions, but only in a strictly sequential order.
- **Value:** an infix expression using names of constants, dimensions, and already-defined expressions to define a mathematical quantity. May also include bare numeric values. An example would be `(D1+E2)/D3 + 5.2` Assuming `E2` has already been defined. Also supports the following functions:
    - `sin(x)`, `cos(x)`, and `tan(x)`, which implement the trigonometric functions assuming the input quantity is in radians.
    - `sind(x)`, `cosd(x)`, and `tand(x)`, which implement the trigonometric functions assuming the input quantity is in degrees.
- **Lower:** The lower bound that this expression must satisfy to meet requirements. Will be flagged as a failed condition in the output if not met. Leave the cell empty to not set a lower bound.
- **Upper:** The upper bound that this expression must satisfy to meet requirements. Will be flagged as a failed condition in the output if not met. Leave the cell empty to not set an upper bound.
- **M:** the method by which to evaluate the expression. Default is worst-case; other options are:
    - **W:** worst-case evaluation; the nominal value will be propagated, and each operation will be evaluated in a worst-case sense. The output tolerance will be reported as plus/minus values from the nominal output value.
    - **1S, 2S, 3S:** statistical evaluation at ±1σ, ±2σ, and ±3σ. Each dimension is sampled several times from a distribution as defined in the dimension definition, and then the random samples have each operation applied element wise to simulate the final output in a Monte Carlo sense. The output is reported as the median value, with the -nσ and +nσ values defined by quantiles on the distribution such that the tails are equally weighted and have the same total weight as the tails in a normal distribution beyond ±nσ.
- **Note:** Arbitrary unicode text for documentation.

### Output Options

- **Where Used:** Will print below each dimension definition in the output which expressions are affected by that dimension. Will include any effect, even if the influence is through several layers of expression cross references.
- **Sensitivity:** prints a sensitivity analysis for each expression. This is the partial derivative of the expression nominal value with respect to the dimension. Can be used to determine whether the plus or minus tolerance of a dimension is more critical to meet a particular bound.
- **Tolerance Contribution:** Prints an estimate of how much each dimension contributes to the overall tolerance of the expression. Computed by looping though all dimensions that an expression depends on, recomputing the expression with that dimension set to have zero tolerance, and evaluating the reduction in total tolerance range of the expression. Can be used to determine which dimensions are most important to refine to meet a particular bound.

For more details, visit the [GitHub repository](https://github.com/lemon1324/tolstack).
