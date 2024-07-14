## Introduction

`tolstack` is designed to assist with tolerance analysis for engineering design.

## Features

- Allows definition of dimensions with uniform or normal distributions.
- Associates part numbers and comments to dimensions for traceability.
- Implements addition, subtraction, multiplication, division, and exponentiation.
- Expression parser also handles parentheses and unary negation.
- Expressions can be evaluated in either worst-case or statistical modes against lower and/or upper bounds.
-

## Using the Application

1. Step-by-step instructions on how to use the application.
2. Additional information.

## FAQ

- **How do I analyze geometric tolerances?**

  As geometric tolerances generally require full knowledge of the geometry to analyze, they are not currently set up to be natively analyzed in `tolstack`.

  However, as `tolstack` implements mathematical operations beyond addition, many geometric tolerances can be analyzed by decomposing them to equivalent +/- tolerances and composing them.

  For example, suppose we have a street sign of height H = 90 in +/- 5%, with a mounting flange of diameter D = 6 in +/- 0.25 in. Let's say the flange has a perpendicularity to the pole of 0.1". To determine how much the top of the pole can shift laterally, we can define an equivalent +/- tolerance T and multiply by H/D to get the motion of the top of the pole.

  Note that since the perpendicularity tolerance allows either the left side or the right side to be raised by .1" with respect to the other, the equivalent tolerance used in this example should be +/-0.1.

  See the `street_sign` example in `examples` in the [GitHub repository](https://github.com/lemon1324/tolstack) for the worked example file.

- **What does ±3σ actually mean?**

  For dimension inputs, this is the normal definition of standard deviation: the underlying distribution for that dimension will be normal, with a mean and standard distribution such that ±3σ matches the range from the minus tolerance to the plus tolerance.

  For expressions, since the underlying distribution may not be normal in several cases, the end points are defined as quantiles of the output distribution. The quantiles are defines to have equal weight in the tails, and to have 99.7% between the tails, just as for a normal distribution at ±3σ.

For more details, visit the [GitHub repository](https://github.com/lemon1324/tolstack).
