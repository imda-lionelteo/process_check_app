import re
from typing import Any, Optional

import pandas as pd
from pandas import DataFrame, ExcelFile, Series
from streamlit.logger import get_logger

logger = get_logger(__name__)

# Define constant for AI type
SELECTED_AI_TYPE: str = "Generative AI"


def extract_principle_description(df: DataFrame) -> str:
    """
    Extract the principle description from the DataFrame.

    Args:
        df: DataFrame containing the principle data

    Returns:
        The principle description as a string
    """
    return str(df.iloc[0, 0])


def is_valid_process_id(process_id: Any) -> bool:
    """
    Check if the process ID has a valid format.

    Args:
        process_id: The process ID to validate

    Returns:
        True if the process ID is valid, False otherwise
    """
    return (
        isinstance(process_id, (str, int, float))
        and re.match(r"^\d+\.\d+\.\d+$", str(process_id)) is not None
    )


def load_principles_data(excel_file_path: str) -> dict[str, dict[str, Any]]:
    """
    Load AI principles data from an Excel file.

    Args:
        excel_file_path: Path to the Excel file with principles data

    Returns:
        Dictionary of principles data
    """
    excel_data = pd.ExcelFile(excel_file_path)
    return process_excel_principles_data(excel_data)


def matches_ai_type_filter(type_of_ai: Any, ai_type_filter: str) -> bool:
    """
    Check if the AI type matches the filter.

    Args:
        type_of_ai: The AI type from the row
        ai_type_filter: The AI type to filter by

    Returns:
        True if the AI type matches the filter, False otherwise
    """
    return isinstance(type_of_ai, str) and ai_type_filter in type_of_ai


def parse_process_check_row(
    row: Series, merged_cell_values: dict[str, Any], ai_type_filter: str
) -> Optional[dict[str, Any]]:
    """
    Parse a row from the process check spreadsheet, handling merged cells.

    Args:
        row: A DataFrame row containing process check data
        merged_cell_values: Values from merged cells carried over from previous rows
        ai_type_filter: The AI type to filter questions by

    Returns:
        Process check data from the row or None if invalid
    """
    # Get values from the row or from merged cells
    outcome_id = merged_cell_values["outcome_id"]
    type_of_ai = merged_cell_values["type_of_ai"]
    outcomes = merged_cell_values["outcomes"]
    process_id = row.iloc[3]

    # Validate process ID format
    if not is_valid_process_id(process_id):
        return None

    # Filter by AI type
    if not matches_ai_type_filter(type_of_ai, ai_type_filter):
        return None

    return {
        "outcome_id": outcome_id,
        "type_of_ai": type_of_ai,
        "outcomes": outcomes,
        "process_to_achieve_outcomes": row.iloc[4] if pd.notna(row.iloc[4]) else "",
        "nature_of_evidence": row.iloc[5] if pd.notna(row.iloc[5]) else "",
        "evidence": row.iloc[6] if pd.notna(row.iloc[6]) else "",
    }


def process_excel_principles_data(excel_data: ExcelFile) -> dict[str, dict[str, Any]]:
    """
    Process the Excel file and extract principle data with process checks.

    Args:
        excel_data: The Excel file data

    Returns:
        Dictionary of principles with their descriptions and process checks
    """
    principles_data = {}

    for sheet_name in excel_data.sheet_names:
        if "Instructions" in str(sheet_name):
            continue

        df = excel_data.parse(sheet_name)
        principle_data = process_principle_sheet(df, sheet_name)

        if principle_data:
            principles_data[str(sheet_name)] = principle_data

    logger.info(f"Extracted data for {len(principles_data)} principles")
    return principles_data


def process_principle_sheet(df: DataFrame, sheet_name: Any) -> Optional[dict[str, Any]]:
    """
    Process a single principle sheet from the Excel file.

    Args:
        df: DataFrame containing the principle data
        sheet_name: Name of the sheet being processed

    Returns:
        Dictionary with principle description and process checks, or None if error
    """
    try:
        principle_description = extract_principle_description(df)
        process_checks = {}
        merged_cell_values = {
            "outcome_id": None,
            "type_of_ai": None,
            "outcomes": None,
        }

        for index, row in df.iterrows():
            if isinstance(index, int) and index < 1:  # Skip header row
                continue

            # Update merged cell values
            merged_cell_values = update_merged_cell_values(row, merged_cell_values)

            # Parse the row data
            process_check = parse_process_check_row(
                row, merged_cell_values, SELECTED_AI_TYPE
            )

            # Add valid process checks to the collection
            if process_check and process_check["process_to_achieve_outcomes"]:
                process_checks[str(row.iloc[3])] = process_check

        # Return principle data if it has process checks
        if process_checks:
            return {
                "principle_description": principle_description,
                "process_checks": process_checks,
            }
        return None

    except Exception as e:
        logger.error(f"Error processing principle sheet {sheet_name}: {str(e)}")
        return None


def update_merged_cell_values(
    row: Series, merged_cell_values: dict[str, Any]
) -> dict[str, Any]:
    """
    Update the merged cell values dictionary with non-NA values from the current row.

    Args:
        row: A DataFrame row containing process check data
        merged_cell_values: Values from merged cells carried over from previous rows

    Returns:
        Updated merged cell values dictionary
    """
    # Create a copy to avoid modifying the original
    updated_values = merged_cell_values.copy()

    # Update values if they exist in the current row
    updated_values["outcome_id"] = (
        row.iloc[0] if pd.notna(row.iloc[0]) else merged_cell_values["outcome_id"]
    )
    updated_values["type_of_ai"] = (
        row.iloc[1] if pd.notna(row.iloc[1]) else merged_cell_values["type_of_ai"]
    )
    updated_values["outcomes"] = (
        row.iloc[2] if pd.notna(row.iloc[2]) else merged_cell_values["outcomes"]
    )

    return updated_values
