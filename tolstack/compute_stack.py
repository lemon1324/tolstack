from tolstack.StackParser import StackParser

from tolstack.StackFormat import (
    format_constant,
    format_constant_header,
    format_dimension,
    format_dimension_header,
    format_expression,
)

import matplotlib.pyplot as plt
import numpy
import scipy

import sys

import argparse


def main():
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Process a text file defining tolerance expressions and print result to console or a file."
    )
    parser.add_argument(
        "filename", type=str, nargs="?", help="The input file to process."
    )
    parser.add_argument(
        "-o", "--output", type=str, help="The file to save the human-readable output."
    )
    # parser.add_argument(
    #     "-c", "--csv-output", type=str, help="The file to save a CSV report."
    # )
    parser.add_argument(
        "-S",
        "--sensitivity-analysis",
        action="store_true",
        help="Conduct input sensitivity analysis",
    )
    parser.add_argument(
        "-T",
        "--tolerance-contribution",
        action="store_true",
        help="Conduct tolerance contribution analysis",
    )

    # Parse the arguments
    args = parser.parse_args()

    infile = args.filename
    output_file = args.output
    # csv_output_file = args.csv_output
    conduct_sensitivity_analysis = args.sensitivity_analysis
    conduct_tolerance_contribution = args.tolerance_contribution

    if not infile:
        parser.print_help()
        sys.exit(0)

    SP = StackParser()
    print_lines = []

    if conduct_sensitivity_analysis:
        print_lines.append(
            "**WARN: Sensitivity analysis not yet implemented, ignoring."
        )

    if conduct_tolerance_contribution:
        print_lines.append(
            "**WARN: Tolerance contribution analysis not yet implemented, ignoring."
        )

    try:
        with open(infile, "r") as file:
            lines = file.readlines()

        SP.parse(lines)

        value_map = SP.constants | SP.dimensions

        print_lines.append("CONSTANTS:")
        print_lines.append(format_constant_header())
        for key, C in SP.constants.items():
            print_lines.append(format_constant(C, SP.where_used))

        print_lines.append("DIMENSIONS:")
        print_lines.append(format_dimension_header())
        for key, D in SP.dimensions.items():
            print_lines.append(format_dimension(D, SP.where_used))

        print_lines.append("EXPRESSIONS:")
        for key, SE in SP.expressions.items():
            print_lines.append(format_expression(SE))

        if output_file:
            with open(output_file, "w") as out_file:
                for line in print_lines:
                    out_file.write(line)
        else:
            # Print the content to the console if no output file is specified
            for line in print_lines:
                print(line)
            pass

    except FileNotFoundError:
        print(f"Error: The file '{infile}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # dimA = StackDim(1, 0.01, -0.01, PN="PRT-00231", note="Test Note.")
    # dimB = StackDim(2., 0.0, -0.01, PN="425-00192", note="Another note.")
    # dimC = dimA + dimB
    # dimD = dimA + dimA + dimA + dimA + dimA
    # print(dimA)
    # print(dimD)

    # p = scipy.stats.norm.cdf(-3)
    # print(f"p is {p:.6f}")
    # q = np.quantile(
    #     dimD.data,
    #     [scipy.stats.norm.sf(2), scipy.stats.norm.cdf(2)],
    #     method="median_unbiased",
    # )
    # print(f"+/-2sig range is {q[0]:.4f}, {q[1]:.4f}")
    # t = timeit.repeat(
    #     "dimA+dimA",
    #     setup="dimA = StackDim(1, 0.01, -0.01)",
    #     repeat=1000,
    #     number=1,
    #     globals=globals(),
    # )

    # print(f"time taken: {1000*np.mean(t):.3f} ms")

    # counts, bins = np.histogram(dimD.data, bins=29)
    # plt.hist(bins[:-1], bins, weights=counts)
    # plt.show()

    main()
