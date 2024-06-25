import argparse

from tolstack.StackParser import StackParser

from tolstack.StackFormat import (
    format_constant,
    format_constant_header,
    format_dimension,
    format_dimension_header,
    format_expression,
)


def process_files(
    input_file,
    output_file,
    conduct_sensitivity_analysis,
    conduct_tolerance_contribution,
):
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
        with open(input_file, "r") as file:
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
            with open(output_file, "w", encoding="utf-8") as out_file:
                for line in print_lines:
                    out_file.write(line + "\n")
        else:
            # Print the content to the console if no output file is specified
            for line in print_lines:
                print(line)
            pass

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
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

    input_file = args.filename
    output_file = args.output
    conduct_sensitivity_analysis = args.sensitivity_analysis
    conduct_tolerance_contribution = args.tolerance_contribution

    process_files(
        input_file,
        output_file,
        conduct_sensitivity_analysis,
        conduct_tolerance_contribution,
    )
