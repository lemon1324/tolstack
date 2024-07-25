import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Image,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from pathlib import Path


# Helper function to convert a plot into an image suitable for ReportLab
def generate_dist_plot(
    data_object,
    width=800,
    height=600,
    axis_font_size=10,
    dpi=300,
    line_weight=1,
    spine_linewidth=1,
):
    # Extracting data for points and statistical lines
    points = data_object[
        "data"
    ]  # Assuming data_object contains a 'data' key with a numpy array
    l = data_object["l"]
    lb = data_object["lb"]
    m = data_object["m"]
    ub = data_object["ub"]
    u = data_object["u"]

    # Creating the plot with specified dimensions and font sizes
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=dpi)
    ax.hist(points, bins=20, color="lightgrey", edgecolor="none")

    # Adjust the thickness of the lines surrounding the plot area
    for spine in ax.spines.values():
        spine.set_linewidth(spine_linewidth)

    # Drawing vertical lines at specified points with adjustable line weight
    ax.axvline(l, color="red", linestyle="--", linewidth=line_weight, label="l, u")
    ax.axvline(u, color="red", linestyle="--", linewidth=line_weight)

    ax.axvline(lb, color="blue", linestyle="--", linewidth=line_weight, label="lb, ub")
    ax.axvline(ub, color="blue", linestyle="--", linewidth=line_weight)

    ax.axvline(m, color="green", linestyle="-", linewidth=line_weight, label="m")

    # Remove y-axis label and tick marks
    ax.set_yticks([])
    ax.set_ylabel("")

    # Display only 3 x tick marks and remove x label
    ax.set_xticks(
        [
            ax.get_xticks()[0],
            (ax.get_xticks()[0] + ax.get_xticks()[-1]) / 2,
            ax.get_xticks()[-1],
        ]
    )
    ax.set_xlabel("")

    # Setting the font sizes for the ticks
    ax.tick_params(axis="x", labelsize=axis_font_size)

    # Adding a legend for the vertical lines
    # ax.legend()

    # Adjust layout to ensure the labels are not cut off
    plt.tight_layout()

    # Saving the plot to a BytesIO buffer with higher DPI for better quality
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=dpi)
    plt.close(fig)

    buf.seek(0)
    return buf


# Helper function to create flowables from a data object
def create_flowables(data_object, include_graphs=False, include_images=False):
    styles = getSampleStyleSheet()

    # Paragraph content
    paragraph_content = [
        Paragraph(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            styles["BodyText"],
        ),
        Paragraph(
            "Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae;",
            styles["BodyText"],
        ),
    ]

    if include_graphs:
        aspect_ratio = 4
        height = 0.67
        dpi = 300

        graph_image = generate_dist_plot(
            data_object,
            width=height * aspect_ratio * dpi,
            height=height * dpi,
            axis_font_size=20,
            line_weight=5,
            dpi=dpi,
            spine_linewidth=2,
        )

        graph = Image(
            graph_image, width=height * aspect_ratio * inch, height=height * inch
        )

        # Create table with paragraphs on the left and the image on the right
        table_data = [[paragraph_content[0], graph]]
        col_widths = [None, height * aspect_ratio * inch]
        table = Table(table_data, colWidths=col_widths)

        # Add table style to control alignment and spacing
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (0, 0), 0),
                    ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ]
            )
        )

        flowables = [table]
    else:
        flowables = paragraph_content[
            :1
        ]  # if no graph included, keep only the first paragraph

    flowables.append(Spacer(1, 12))
    flowables.append(paragraph_content[1])  # always add the second paragraph

    if include_images:
        pass  # do image lookup stuff here

    return flowables


# Helper function to get the lowest level folder containing a file
def get_lowest_level_folder(filename):
    path = Path(filename).resolve()
    return path.parent


# Helper function to search for a .png file and return the image data
def find_png_image(folder, name):
    image_path = folder / f"{name}.png"
    if image_path.exists():
        with open(image_path, "rb") as img_file:
            return img_file.read()
    return None


# Primary function to format and generate the PDF
def format_pdf(
    output_filename, data_structure, include_graphs=False, include_images=False
):
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    flowables = create_flowables(data_structure, include_graphs, include_images)
    doc.build(flowables)


# Example usage
if __name__ == "__main__":
    # Mock data structure for illustration
    data_structure = {
        "data": np.random.randn(1000),
        "l": -2,
        "lb": -1,
        "m": 0,
        "ub": 1,
        "u": 2,
    }

    output_filename = "test_outputs/example_report.pdf"
    format_pdf(output_filename, data_structure, include_graphs=True)
