import argparse

import logging

from tolstack.StackParser import StackParser

from tolstack.gui.FormatText import format_text
from tolstack.gui.FormatPDF import format_pdf

from tolstack.gui.FileIO import open_from_name
from tolstack.gui.GUITypes import OptionsWidget, DataWidget


def process_info(info):
    SP = StackParser()
    SP.parse(
        constants_data=info[DataWidget.CONSTANTS],
        dimensions_data=info[DataWidget.DIMENSIONS],
        expressions_data=info[DataWidget.EXPRESSIONS],
    )

    print_lines = format_text(SP, info)
    return print_lines


def process_info_to_pdf(info, filename):
    SP = StackParser()
    SP.parse(
        constants_data=info[DataWidget.CONSTANTS],
        dimensions_data=info[DataWidget.DIMENSIONS],
        expressions_data=info[DataWidget.EXPRESSIONS],
    )

    format_pdf(output_filename=filename, parser=SP, info=info)


def process_file(
    input_file,
    output_file,
    print_usage,
    conduct_sensitivity_analysis,
    conduct_tolerance_contribution,
):
    try:
        info = open_from_name(input_file)
        info[OptionsWidget.WHERE_USED] = print_usage
        info[OptionsWidget.SENSITIVITY] = conduct_sensitivity_analysis
        info[OptionsWidget.CONTRIBUTIONS] = conduct_tolerance_contribution

        SP = StackParser()
        SP.parse(
            constants_data=info[DataWidget.CONSTANTS],
            dimensions_data=info[DataWidget.DIMENSIONS],
            expressions_data=info[DataWidget.EXPRESSIONS],
        )

        print_lines = format_text(SP, info)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as out_file:
                for line in print_lines:
                    out_file.write(line + "\n")
        else:
            # Print the content to the console if no output file is specified
            for line in print_lines:
                print(line)

    except FileNotFoundError:
        logging.error(f"Error: The file '{input_file}' was not found.", exc_info=True)
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        print(f"An error occurred: {e}")


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
        "-U",
        "--usage",
        action="store_true",
        help="Print usage of dimensions in expressions",
    )
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
    print_usage = args.usage
    conduct_sensitivity_analysis = args.sensitivity_analysis
    conduct_tolerance_contribution = args.tolerance_contribution

    process_file(
        input_file,
        output_file,
        print_usage,
        conduct_sensitivity_analysis,
        conduct_tolerance_contribution,
    )
