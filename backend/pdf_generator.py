import os
from datetime import datetime

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from backend.principle_calculator import process_principle
from backend.report_validation import get_report_info
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

LOGO_PATH = "assets/aiverify_logo.png"
GENERATED_REPORT_NAME = "summary_report.pdf"


def add_page_number(canvas, doc):
    """
    Adds a page number to the bottom right corner of each page, except the first page.

    Args:
        canvas: The canvas object to draw on.
        doc: The document object containing page information.
    """
    if doc.page > 1:
        page_number_text = f"Page {doc.page}"
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(
            doc.pagesize[0] - 0.5 * inch,  # Right margin
            0.5 * inch,  # Bottom margin
            page_number_text,
        )
        canvas.restoreState()


def add_title(elements, company_name):
    """
    Adds a title, company name, and date to the PDF elements list.

    Args:
        elements: The list of elements to add to the PDF.
        company_name: The name of the company to display.
    """
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=50,
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    title = Paragraph("Summary Report", title_style)
    elements.append(title)

    elements.append(Spacer(1, 0.5 * inch))

    date_generated = datetime.now().strftime("%B %d, %Y")

    company_name_style = ParagraphStyle(
        "CompanyNameStyle",
        parent=styles["Normal"],
        fontSize=16,
        spaceAfter=6,
        alignment=TA_RIGHT,
    )
    date_generated_style = ParagraphStyle(
        "DateGeneratedStyle", parent=styles["Normal"], fontSize=12, alignment=TA_RIGHT
    )

    company_name_paragraph = Paragraph(f"<b>{company_name}</b>", company_name_style)
    date_generated_paragraph = Paragraph(date_generated, date_generated_style)

    elements.append(company_name_paragraph)
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(date_generated_paragraph)


def draw_logo(canvas, doc):
    """
    Draws the company logo at the bottom right corner of the first page.

    Args:
        canvas: The canvas object to draw on.
        doc: The document object containing page information.
    """
    width, height = letter
    if doc.page == 1:
        logo = Image(LOGO_PATH)
        original_width, original_height = logo.wrap(0, 0)

        aspect_ratio = original_width / original_height

        desired_width = 3 * inch
        desired_height = desired_width / aspect_ratio

        logo.drawWidth = desired_width
        logo.drawHeight = desired_height
        logo.drawOn(canvas, width - desired_width - 0.5 * inch, 0.5 * inch)


def add_second_page(elements, workspace_data, doc):
    """
    Adds the second page content to the PDF elements list, including the aim of AI Verify,
    use case details, and scope of checks.

    Args:
        elements: The list of elements to add to the PDF.
        workspace_data: The data containing information about the workspace.
        doc: The document object containing page information.
    """
    styles = getSampleStyleSheet()

    elements.append(PageBreak())

    aim_title = Paragraph(
        "<b>Aim of AI Verify Testing Framework for Generative AI</b>",
        styles["Heading2"],
    )
    aim_content = Paragraph(
        "AI Verify aims to help organisations validate the performance of their AI "
        "systems against a set of internationally recognised principles and document "
        "that their AI systems have been developed and deployed with processes designed "
        "to achieve the desired outcomes of these principles.",
        styles["Normal"],
    )
    elements.append(aim_title)
    elements.append(aim_content)
    elements.append(Spacer(1, 12))

    intro_text = Paragraph(
        "Companies can use this report to:",
        styles["Normal"],
    )
    elements.append(intro_text)

    bullet_points = ListFlowable(
        [
            ListItem(
                Paragraph(
                    "Identify potential gaps and take appropriate actions to address "
                    "them, where applicable.",
                    styles["Normal"],
                )
            ),
            ListItem(
                Paragraph(
                    "Demonstrate their implementation of responsible AI practices and "
                    "build trust with their stakeholders.",
                    styles["Normal"],
                )
            ),
        ],
        bulletType="bullet",
        start="circle",
        bulletFontSize=4,
    )
    elements.append(bullet_points)
    elements.append(Spacer(1, 12))

    note_content = Paragraph(
        "<b>Please note that only reports generated by AI Verify-Project Moonshot "
        "toolkit, in accordance with the AI Verify Testing Framework, and without any "
        "modification, are considered AI Verify reports.</b>",
        styles["Normal"],
    )
    elements.append(note_content)
    elements.append(Spacer(1, 12))

    app_name = workspace_data.get("app_name", "Unknown Application")
    app_description = workspace_data.get("app_description", "No description available.")

    use_case_title = Paragraph("<b>Details of Use Case</b>", styles["Heading2"])
    use_case_content = Paragraph(
        f"Name of application tested: {app_name}<br/>"
        f"Purpose of the use case/application: {app_description}",
        styles["Normal"],
    )

    use_case_table = Table(
        [[use_case_title], [use_case_content]],
        colWidths=[doc.width],
    )
    use_case_table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    elements.append(use_case_table)
    elements.append(Spacer(1, 12))

    scope_title = Paragraph(
        "<b>Scope of Checks and Technical Tests</b>", styles["Heading2"]
    )
    scope_content = Paragraph(
        "This summary report provides an overview of how the AI system performs "
        "vis-à-vis the AI Verify Testing Framework for Generative AI. The Framework "
        "covers 11 AI governance principles: ",
        styles["Normal"],
    )
    elements.append(scope_title)
    elements.append(scope_content)

    principles_list = ListFlowable(
        [
            ListItem(Paragraph("Transparency", styles["Normal"])),
            ListItem(Paragraph("Explainability", styles["Normal"])),
            ListItem(Paragraph("Repeatability / Reproducibility", styles["Normal"])),
            ListItem(Paragraph("Safety", styles["Normal"])),
            ListItem(Paragraph("Security", styles["Normal"])),
            ListItem(Paragraph("Robustness", styles["Normal"])),
            ListItem(Paragraph("Fairness", styles["Normal"])),
            ListItem(Paragraph("Data Governance", styles["Normal"])),
            ListItem(Paragraph("Accountability", styles["Normal"])),
            ListItem(Paragraph("Human Agency and Oversight", styles["Normal"])),
            ListItem(
                Paragraph(
                    "Inclusive Growth, Societal and Environmental Well-being",
                    styles["Normal"],
                )
            ),
        ],
        bulletType="1",
        start="1",
        bulletFontSize=10,
        bulletFormat="%s.",
    )
    elements.append(principles_list)


def compile_results(json_data):
    """
    Compiles the results from JSON data into overall statistics and principle-specific statistics.

    Args:
        json_data: The JSON data containing process information.

    Returns:
        A tuple containing overall statistics and principle-specific statistics.
    """
    overall_yes_count = 0
    overall_no_count = 0
    overall_na_count = 0

    principle_stats = {}

    for outcome_id, processes in json_data.items():
        for process_id, process_info in processes.items():
            principle_key = process_info.get(
                "principle_key", "Unknown Principle"
            ).strip()

            if principle_key not in principle_stats:
                principle_stats[principle_key] = {"Yes": 0, "No": 0, "N/A": 0}

            implementation_status = process_info.get("implementation", "N/A")
            if implementation_status == "Yes":
                overall_yes_count += 1
                principle_stats[principle_key]["Yes"] += 1
            elif implementation_status == "No":
                overall_no_count += 1
                principle_stats[principle_key]["No"] += 1
            elif implementation_status == "N/A":
                overall_na_count += 1
                principle_stats[principle_key]["N/A"] += 1

    overall_stats = {
        "Total Yes": overall_yes_count,
        "Total No": overall_no_count,
        "Total N/A": overall_na_count,
    }

    return overall_stats, principle_stats


def add_overview_completion_status(elements, process_checks, test_result_info):
    """
    Adds an overview of the completion status to the PDF elements list, including a donut chart
    and descriptive text.

    Args:
        elements: The list of elements to add to the PDF.
        process_checks: The process checks data.
        test_result_info: The test result information.
    """
    elements.append(PageBreak())

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Normal"],
        fontSize=14,
        leading=16,
        spaceAfter=12,
        alignment=TA_LEFT,
    )

    elements.append(Paragraph("Overall Completion Status", title_style))

    overall_stats, principle_stats = compile_results(process_checks)

    total_answered = sum(overall_stats.values())
    yes_count = overall_stats.get("Total Yes", 0)
    no_count = overall_stats.get("Total No", 0)
    na_count = overall_stats.get("Total N/A", 0)

    sizes = [yes_count, no_count, na_count]
    colors = ["#1E90FF", "#FF8C00", "#32CD32"]

    filtered_sizes = [size for size in sizes if size > 0]
    filtered_colors = [color for color, size in zip(colors, sizes) if size > 0]
    filtered_labels = [
        label for label, size in zip(["Yes", "No", "N/A"], sizes) if size > 0
    ]

    fig, ax = plt.subplots(figsize=(8, 8))

    wedges, texts, autotexts = ax.pie(
        filtered_sizes,
        labels=filtered_labels,
        colors=filtered_colors,
        startangle=90,
        autopct=lambda p: f"{int(p * sum(filtered_sizes) / 100)}",
        pctdistance=0.8,
        textprops=dict(color="white", fontsize=18, weight="bold"),
        wedgeprops=dict(edgecolor="white", linewidth=2),
    )

    centre_circle = plt.Circle((0, 0), 0.60, fc="white")
    fig.gca().add_artist(centre_circle)

    ax.text(
        0,
        0,
        "Process Checks",
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=24,
        weight="bold",
    )

    ax.axis("equal")
    plt.tight_layout()

    legend_handles = [
        mpatches.Patch(color="#1E90FF", label="Yes"),
        mpatches.Patch(color="#FF8C00", label="No"),
        mpatches.Patch(color="#32CD32", label="N/A"),
    ]
    ax.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.25),
        ncol=3,
        fontsize=24,
        frameon=True,
        borderpad=1.0,
        labelspacing=1.75,
    )

    chart_filename = "temp_report/overview_completion_status_donut_chart.png"
    plt.savefig(chart_filename, format="png", bbox_inches="tight", dpi=300)
    plt.close()

    chart_image = Image(chart_filename, width=3 * inch, height=3.5 * inch)

    description_intro = f"The company has completed the process checklist of {total_answered} process checks, of which:"
    description_intro_paragraph = Paragraph(description_intro, styles["Normal"])

    description_items = [
        f'<b>{yes_count} process checks</b> are indicated as "Yes", meaning that '
        "the Company has documentary evidence for the implementation.",
        f'<b>{no_count} process checks</b> are indicated as "No", meaning that '
        "the Company has not implemented them.",
        f'<b>{na_count} process checks</b> are indicated as "Not Applicable", '
        "meaning that the Company has not implemented them because these processes "
        "are not applicable to the AI system being tested.",
    ]

    description_list = ListFlowable(
        [Paragraph(item, styles["Normal"]) for item in description_items],
        bulletType="bullet",
    )

    side_by_side_table_data = [
        [chart_image, [description_intro_paragraph, description_list]]
    ]
    side_by_side_table = Table(
        side_by_side_table_data, colWidths=[3.5 * inch, 4.5 * inch]
    )

    side_by_side_table.setStyle(
        TableStyle(
            [
                (
                    "ALIGN",
                    (1, 0),
                    (1, 0),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (1, 0),
                    (1, 0),
                    "MIDDLE",
                ),
            ]
        )
    )

    elements.append(Spacer(1, 12))
    elements.append(side_by_side_table)
    elements.append(Spacer(1, 12))
    alignment_text = (
        "<b>Alignment with other international frameworks</b><br/>"
        "By completing the AI Verify testing framework for Generative AI, "
        "which is mapped to Hiroshima Process International Code of Conduct "
        "for Organizations Developing Advanced AI Systems (CoC) and US National "
        "Institute of Standards and Technology’s (NIST) Artificial Intelligence "
        "Risk Management Framework Profile (AI RMF): Generative Artificial "
        "Intelligence, the Company has assessed its responsible AI practices against "
        "these frameworks as well. AI Verify processes that are mapped to these "
        "frameworks will have respective labels e.g. “Hiroshima Process CoC” or “US "
        "NIST AI RMF” next to them."
    )

    alignment_paragraph = Paragraph(alignment_text, styles["Normal"])
    elements.append(alignment_paragraph)
    elements.append(Spacer(1, 8))

    technical_test_header = Paragraph("Technical Test", styles["Heading2"])
    elements.append(technical_test_header)

    if not test_result_info:
        no_test_paragraph = Paragraph(
            "<b>No technical test uploaded.</b>", styles["Normal"]
        )
        elements.append(no_test_paragraph)
        elements.append(Spacer(1, 4))
    else:
        test_success = test_result_info["total_tests"]["test_success"]
        test_fail = test_result_info["total_tests"]["test_fail"]
        test_skip = test_result_info["total_tests"]["test_skip"]

        test_results_data = [
            (
                f"Test Successfully Run: {test_success}",
                "",
                "#228B22",
            ),
            (f"Test Failed to Complete: {test_fail}", "", "#FF0000"),
            (f"Test Skipped: {test_skip}", "", "#A9A9A9"),
        ]

        box_tables = []

        box_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), "#f9f9f9"),
                ("TEXTCOLOR", (0, 0), (-1, -1), "#000000"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOX", (0, 0), (-1, -1), 1, "#e0e0e0"),
                ("PADDING", (0, 0), (-1, -1), 12),
            ]
        )

        for label, value, color in test_results_data:
            box_data = [
                [
                    Paragraph(
                        f'<font color="{color}">{label}</font>',
                        ParagraphStyle("Centered", alignment=TA_CENTER),
                    )
                ],
                [Paragraph(value, ParagraphStyle("Centered", alignment=TA_CENTER))],
            ]
            box_table = Table(box_data, colWidths=[2.5 * inch])
            box_table.setStyle(box_style)
            box_tables.append(box_table)

        side_by_side_table = Table(
            [
                [
                    box_tables[0],
                    Spacer(0.25 * inch, 0),
                    box_tables[1],
                    Spacer(0.25 * inch, 0),
                    box_tables[2],
                ]
            ],
            colWidths=[
                2.5 * inch,
                0.25 * inch,
                2.5 * inch,
                0.25 * inch,
                2.5 * inch,
            ],
            hAlign="CENTER",
        )
        elements.append(side_by_side_table)

        test_names = [
            entry.get("test_name", "Unnamed Test")
            for entry in test_result_info["evaluation_summaries_and_metadata"]
        ]

        test_names_header = Paragraph(
            "Name of Tests Successfully Run:", styles["Heading3"]
        )
        elements.append(test_names_header)
        elements.append(Spacer(1, 4))

        bullet_list = ListFlowable(
            [Paragraph(test_name, styles["Normal"]) for test_name in test_names],
            bulletType="bullet",
            start="circle",
            bulletFontSize=8,
        )
        elements.append(bullet_list)
        elements.append(Spacer(1, 4))


def principle_summary(elements, workspace_data, principle_name, principle_number):
    """
    Adds a summary of a specific principle to the PDF elements list, including a donut chart
    and descriptive text.

    Args:
        elements: The list of elements to add to the PDF.
        workspace_data: The data containing information about the workspace.
        principle_name: The name of the principle to summarize.
        principle_number: The number of the principle.
    """
    elements.append(PageBreak())

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=14,
        spaceAfter=12,
        alignment=TA_LEFT,
    )
    elements.append(Paragraph(principle_name.upper(), title_style))

    data = process_principle(workspace_data, principle_name, principle_number)
    chart_filename = create_donut_chart(data, principle_name)

    chart = Image(chart_filename, width=3 * inch, height=3.5 * inch)

    text_style = ParagraphStyle(
        "TextStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        spaceAfter=6,
        alignment=TA_LEFT,
    )

    if data[principle_name].get("all_yes", False):
        left_content = [chart]
        right_content = []

        right_content.append(
            Paragraph(f"<b>{data[principle_name]['description']}</b>", text_style)
        )

        right_content.append(Spacer(1, 12))
        right_content.append(Paragraph("<b>What It Means:</b>", text_style))
        for wim_text in data[principle_name]["wim"]:
            right_content.append(Paragraph(f"{wim_text}", text_style))
    else:
        left_content = [chart]
        left_content.append(Spacer(1, 12))
        left_content.append(Paragraph("<b>What It Means:</b>", text_style))
        for wim_text in data[principle_name]["wim"]:
            left_content.append(Paragraph(f"{wim_text}", text_style))

        if data[principle_name]["no"] > 0 or data[principle_name]["na"] > 0:
            recommendation = Paragraph(
                f"<b>Recommendation:</b><br/>{data[principle_name]['recommendation']}",
                text_style,
            )
            left_content.append(recommendation)

        right_content = []
        right_content.append(
            Paragraph(f"<b>{data[principle_name]['description']}</b>", text_style)
        )

        if data[principle_name]["no"] > 0 or data[principle_name]["na"] > 0:
            right_content.append(
                Paragraph(
                    "<b>Company did not implement the following testable criteria fully:</b>",
                    text_style,
                )
            )
            for desc in data["process_to_achieve_outcomes"]:
                bullet_points = desc.split("\n")
                for point in bullet_points:
                    indented_point = f"    {point.strip()}"
                    right_content.append(Paragraph(f"• {indented_point}", text_style))
        if not data[principle_name].get("all_yes", False):
            justifications_title = Paragraph("<b>Justifications:</b>", text_style)
            right_content.append(justifications_title)

            justifications = data.get("justifications", None)
            if justifications:
                justification_items = [
                    ListItem(Paragraph(justification, text_style))
                    for justification in justifications
                ]
                justifications_list = ListFlowable(
                    justification_items, bulletType="bullet"
                )
                right_content.append(justifications_list)
            else:
                no_justification_text = Paragraph(
                    '<font color="red">The company did not provide any justification.</font>',
                    text_style,
                )
                right_content.append(no_justification_text)

    table_data = [[left_content, right_content]]
    table = Table(table_data, colWidths=[3.5 * inch, 4.5 * inch])

    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    elements.append(table)

    return elements


def safety_technical_test(elements, test_result_info):
    """
    Adds a safety technical test section to the PDF elements list, including a table of test results
    and descriptive text.

    Args:
        elements: The list of elements to add to the PDF.
        test_result_info: The test result information.
    """
    elements.append(PageBreak())

    title_style = ParagraphStyle(
        "TechnicalTestTitle",
        fontSize=16,
        leading=20,
        spaceAfter=12,
        alignment=TA_LEFT,
    )
    title = Paragraph("Technical Test", title_style)
    elements.append(title)

    description_style = ParagraphStyle(
        "DescriptionStyle",
        fontSize=12,
        leading=15,
        spaceAfter=10,
        alignment=TA_LEFT,
    )
    description = Paragraph(
        "The Company has conducted the following tests:", description_style
    )
    elements.append(description)

    evaluation_summaries_and_metadata = test_result_info.get(
        "evaluation_summaries_and_metadata", []
    )

    table_data = []

    table_data.append(["Test Name", "Score"])

    for entry in evaluation_summaries_and_metadata:
        test_name = entry.get("test_name", "Unknown Test")
        score = entry.get("summary", "N/A")

        table_data.append([test_name, score])
    table = Table(table_data, colWidths=[4 * inch, 3 * inch])

    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    colors.black,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.black,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke,
                ),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 12))

    what_it_means_text = (
        "<b>What It Means:</b><br/>"
        "The tests conducted can provide valuable insights into the AI application’s performance and "
        "safety. Each test is accompanied by a score, with the interpretation varying: in some cases, "
        "higher scores indicate better performance or reliability, while in others, lower scores are "
        "preferable (e.g., fewer adverse outcomes or successful prompt injections)."
    )
    what_it_means_paragraph = Paragraph(
        what_it_means_text, getSampleStyleSheet()["Normal"]
    )
    elements.append(what_it_means_paragraph)
    elements.append(Spacer(1, 12))

    recommendation_text = (
        "<b>Recommendation:</b><br/>"
        "The test results highlight areas for improvement. High performance or low risk scores "
        "suggest the AI system is performing well or safe in those areas, while lower performance or "
        "higher risk scores indicate potential risks that could impact business operations or expose the "
        "Company to safety issues. Company would need to assess if the test score is acceptable "
        "according to Company’s risk tolerance level."
    )
    recommendation_paragraph = Paragraph(
        recommendation_text, getSampleStyleSheet()["Normal"]
    )
    elements.append(recommendation_paragraph)
    elements.append(Spacer(1, 12))

    return elements


def create_donut_chart(data, principle_name):
    """
    Creates a donut chart for a specific principle and saves it as an image.

    Args:
        data: The data containing information about the principle.
        principle_name: The name of the principle.

    Returns:
        The filename of the saved donut chart image.
    """
    sizes = [
        data[principle_name]["yes"],
        data[principle_name]["no"],
        data[principle_name]["na"],
    ]
    colors = ["#1E90FF", "#FF8C00", "#32CD32"]

    filtered_sizes = [size for size in sizes if size > 0]
    filtered_colors = [color for color, size in zip(colors, sizes) if size > 0]

    fig, ax = plt.subplots(figsize=(8, 8))

    wedges, texts, autotexts = ax.pie(
        filtered_sizes,
        colors=filtered_colors,
        startangle=90,
        autopct=lambda p: f"{int(p * sum(filtered_sizes) / 100)}",
        pctdistance=0.8,
        textprops=dict(color="white", fontsize=18, weight="bold"),
        wedgeprops=dict(edgecolor="white", linewidth=2),
    )

    centre_circle = plt.Circle((0, 0), 0.60, fc="white")
    fig.gca().add_artist(centre_circle)

    font_size = 24 if len(principle_name) <= 20 else 18
    ax.text(
        0,
        0,
        principle_name.capitalize(),
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=font_size,
        weight="bold",
        wrap=True,
    )

    ax.axis("equal")
    plt.tight_layout()

    legend_handles = [
        mpatches.Patch(color="#1E90FF", label="Yes"),
        mpatches.Patch(color="#FF8C00", label="No"),
        mpatches.Patch(color="#32CD32", label="N/A"),
    ]

    ax.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.25),
        ncol=3,
        fontsize=24,
        frameon=True,
        borderpad=1.0,
        labelspacing=1.75,
    )
    chart_filename = f"temp_report/{principle_name}_donut_chart.png"
    plt.savefig(chart_filename, format="png", bbox_inches="tight", dpi=300)
    plt.close()

    return chart_filename


def add_process_checks(elements, workspace_data):
    """
    Adds a section for process checks to the PDF elements list, including tables of process information.

    Args:
        elements: The list of elements to add to the PDF.
        workspace_data: The data containing information about the workspace.
    """
    styles = getSampleStyleSheet()

    elements.append(PageBreak())
    elements.append(Paragraph("<b>Annex A</b>", styles["Title"]))
    elements.append(Spacer(1, 2 * inch))

    grouped_data = {}
    for outcome_id, processes in workspace_data.get("process_checks", {}).items():
        for process_id, process_info in processes.items():
            principle_key = process_info.get("principle_key", "Unknown Principle")
            if principle_key not in grouped_data:
                grouped_data[principle_key] = {}
            group_key = ".".join(process_id.split(".")[:2])
            if group_key not in grouped_data[principle_key]:
                grouped_data[principle_key][group_key] = []
            grouped_data[principle_key][group_key].append((process_id, process_info))

    for principle_key, groups in grouped_data.items():
        elements.append(PageBreak())
        elements.append(Paragraph(f"<b>{principle_key}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 6))

        for group_key, processes in groups.items():
            outcomes = processes[0][1].get("outcomes", "No outcomes available")
            elements.append(
                Paragraph(f"<b>{group_key} - {outcomes}</b>", styles["Heading3"])
            )
            elements.append(Spacer(1, 6))

            for process_id, process_info in processes:
                elaboration_text = process_info.get("elaboration", "").strip()
                if not elaboration_text:
                    elaboration_text = "&nbsp;" * 255

                data = [
                    [
                        Paragraph(
                            f"<b>{process_id} Process</b><br/>"
                            f"{process_info.get('process_to_achieve_outcomes', '')}",
                            styles["Normal"],
                        ),
                        Paragraph(
                            f"<b>Evidence</b><br/>{process_info.get('evidence', '')}",
                            styles["Normal"],
                        ),
                        Paragraph(
                            f"<b>Implemented</b><br/>"
                            f"{process_info.get('implementation', '')}<br/><br/>"
                            f"<b>Nature of Evidence</b><br/>"
                            f"{process_info.get('nature_of_evidence', '')}",
                            styles["Normal"],
                        ),
                    ],
                    [
                        Paragraph(
                            f"<b>Elaboration</b><br/>{elaboration_text}",
                            styles["Normal"],
                        ),
                        "",
                        "",
                    ],
                ]

                table = Table(data, colWidths=[2.5 * inch, 2.5 * inch, 2 * inch])
                table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                            ("SPAN", (0, 1), (-1, 1)),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTNAME", (0, 1), (-1, 1), "Helvetica"),
                            ("FONTSIZE", (0, 0), (-1, -1), 10),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("MINHEIGHT", (0, 1), (-1, 1), 50),
                        ]
                    )
                )

                elements.append(KeepTogether([table]))
                elements.append(Spacer(1, 12))


def generate_pdf_report(workspace_data):
    """
    Generates a PDF report based on the provided workspace data.

    Args:
        workspace_data: The data containing information about the workspace.

    Returns:
        The file path of the generated PDF report.
    """
    pdf_file_path = os.path.join(os.getcwd(), "temp_report", GENERATED_REPORT_NAME)
    doc = BaseDocTemplate(
        pdf_file_path,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=12,
        bottomMargin=36,
    )
    process_checks = workspace_data["process_checks"]
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height - 1.1 * inch,
        id="normal",
    )
    template = PageTemplate(
        id="test", frames=frame, onPage=draw_logo, onPageEnd=add_page_number
    )
    doc.addPageTemplates([template])

    elements = []

    company_name = workspace_data.get("company_name", "Unknown Company")
    file_path = workspace_data.get("upload_results", {}).get(
        "file_path", "Unknown File Path"
    )

    test_result_info = get_report_info(file_path)

    add_title(elements, company_name)
    add_second_page(elements, workspace_data, doc)
    add_overview_completion_status(elements, process_checks, test_result_info)

    principle_summary(elements, workspace_data, "transparency", "1")
    principle_summary(elements, workspace_data, "explainability", "2")
    principle_summary(elements, workspace_data, "reproducibility", "3")
    principle_summary(elements, workspace_data, "safety", "4")
    if test_result_info:
        safety_technical_test(elements, test_result_info)
    principle_summary(elements, workspace_data, "security", "5")
    principle_summary(elements, workspace_data, "robustness", "6")
    principle_summary(elements, workspace_data, "fairness", "7")
    principle_summary(elements, workspace_data, "data governance", "8")
    principle_summary(elements, workspace_data, "accountability", "9")
    principle_summary(elements, workspace_data, "human agency oversight", "10")
    principle_summary(elements, workspace_data, "inc growth", "11")

    add_process_checks(elements, workspace_data)

    doc.build(elements)

    return pdf_file_path
