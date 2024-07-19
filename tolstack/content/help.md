## About

`tolstack` is designed to assist with tolerance analysis for engineering design.

## Quick Reference

All numeric input fields support any string that can be parsed to a floating point value, including scientific notation. Inclusion or omission of: `+` signs; leading or trailing zeroes; and leading or trailing whitespace is also accepted.

**Name** fields should be 4 characters or fewer, and the recommended format is `Ann` where `A` is a letter and `nn` is a numeral, e.g. `C1`.

### Constants

Constants are defined with a **Name**, used to refer to the constant in expressions, a **Value**, which is the numeric value of the constant, and a **Note**, which is text for documentation.

### Dimensions

Dimensions are defined with a **Name**, used to refer to the dimension in expressions, **Nominal**, **Plus**, and **Minus** values such that the dimension has bounds of `nominal+plus` and `nominal+minus`, a distribution specifier **D**, a part number **PN** for traceability, and a **Note**.

**Note the sign convention for tolerances.** In typical use the value in the minus field should have a '-' sign. The default distribution is uniform (U), and normal distributions (1S, 2S, 3S) may be selected, where ±nσ will be set to span the upper and lower bounds of the dimension.

### Expressions

Defined with **Name**, used to refer to the expression in subsequent expressions,**Value**, an infix expression using bare numeric values and names of constants, dimensions, and expressions to define a mathematical quantity, **Lower** and **Upper** bounds, an evaluation specifier **M**, and a **Note**.

The default method is worst-case (W), though statistical analysis to varying degrees of confidence (1S, 2S, 3S) can be selected to perform a Monte Carlo analysis.

### Output Options

- **Where Used:** Will print below each dimension definition in the output which expressions are affected by that dimension.
- **Sensitivity:** Will print a sensitivity analysis for each expression. This is the partial derivative of the expression nominal value with respect to the dimension. Can be used to determine whether the plus or minus tolerance of a dimension is more critical to meet a particular bound.
- **Tolerance Contribution:** Will print an estimate of how much each dimension contributes to the overall tolerance of the expression. Computed by looping though all dimensions that an expression depends on, recomputing the expression with that dimension set to have zero tolerance, and evaluating the reduction in total tolerance range of the expression. Can be used to determine which dimensions are most important to refine to meet a particular bound.

For more details, visit the [GitHub repository](https://github.com/lemon1324/tolstack).
