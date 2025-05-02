import json
from pathlib import Path
from typing import Optional

import streamlit as st
from streamlit.logger import get_logger

logger = get_logger(__name__)

# Directory where workspace outputs are stored
OUTPUTS_DIRECTORY = Path("sessions")


def initialize(workspace_id: str = "", workspace_data: Optional[dict] = None) -> None:
    """
    Initialize a new workspace session.

    Creates a unique workspace session and sets up the workspace state in Streamlit's session state.
    Ensures the outputs directory exists for storing workspace data.

    Args:
        workspace_id: The identifier for the workspace. Defaults to an empty string.
        workspace_data: The data associated with the workspace. Defaults to None.

    Returns:
        None
    """
    logger.info("Starting the initialization of a new workspace.")

    # Use empty dict as default instead of mutable default argument
    if workspace_data is None:
        workspace_data = {}

    # Create outputs directory if it doesn't exist
    ensure_outputs_directory_exists()

    # Initialize the workspace state
    st.session_state.update(
        {
            "workspace_id": workspace_id,
            "workspace_data": workspace_data,
        }
    )


def workspace_file_exists(workspace_id: str) -> bool:
    """
    Check if a workspace file with the given ID exists on disk.

    Args:
        workspace_id: The workspace ID to check.

    Returns:
        bool: True if the workspace JSON file exists in the outputs directory, False otherwise.
    """
    file_path = OUTPUTS_DIRECTORY / f"{workspace_id}.json"
    return file_path.exists()


def is_workspace_initialized() -> bool:
    """
    Determine if a workspace has been initialized in the current Streamlit session.

    Returns:
        bool: True if a workspace ID is present and non-empty in session state, False otherwise.
    """
    workspace_id = st.session_state.get("workspace_id", "")
    return bool(workspace_id)


def ensure_outputs_directory_exists() -> None:
    """
    Ensure the outputs directory exists for storing workspace data.

    Creates the outputs directory if it doesn't already exist.

    Returns:
        None
    """
    if not OUTPUTS_DIRECTORY.exists():
        OUTPUTS_DIRECTORY.mkdir(parents=True)
        logger.info(f"Outputs directory created: {OUTPUTS_DIRECTORY}")
    else:
        logger.info(f"Outputs directory already exists: {OUTPUTS_DIRECTORY}")


def get_available_workspaces() -> list:
    """
    Retrieve all available workspaces from the outputs directory.

    Scans the outputs directory for JSON files and loads their contents.

    Returns:
        A list of dictionaries containing workspace IDs and their associated data.
    """
    workspaces = []

    # Get all JSON files in the outputs directory
    json_files = list(OUTPUTS_DIRECTORY.glob("*.json"))

    # Process each JSON file
    for file_path in json_files:
        workspace = _load_workspace_file(file_path)
        if workspace:
            workspaces.append(workspace)

    logger.info(f"Total available workspaces found: {len(workspaces)}")
    return workspaces


def _load_workspace_file(file_path: Path) -> Optional[dict]:
    """
    Load a workspace file and return its contents.

    Args:
        file_path: Path to the workspace JSON file

    Returns:
        Dictionary containing workspace ID and data, or None if loading failed
    """
    try:
        with file_path.open("r") as file:
            workspace_data = json.load(file)
            workspace_id = file_path.stem
            return {"workspace_id": workspace_id, "workspace_data": workspace_data}
    except Exception as e:
        logger.error(f"Error reading workspace file {file_path.name}: {str(e)}")
        return None


def load_workspace(workspace_id: str) -> Optional[dict]:
    """
    Load workspace data for a specific workspace ID.

    Attempts to read and parse the JSON file associated with the given workspace ID.

    Args:
        workspace_id: The ID of the workspace to load.

    Returns:
        The workspace data if found, or None if the workspace doesn't exist or cannot be loaded.
    """
    file_path = OUTPUTS_DIRECTORY / f"{workspace_id}.json"

    if not file_path.exists():
        logger.warning(f"Workspace file for ID '{workspace_id}' does not exist.")
        return None

    try:
        with file_path.open("r") as file:
            workspace_data = json.load(file)
            logger.info(f"Workspace data successfully loaded for ID '{workspace_id}'.")
            return workspace_data
    except Exception as e:
        logger.error(f"Error loading workspace data for ID '{workspace_id}': {str(e)}")
        return None


def save_workspace(workspace_id: str, workspace_data: dict) -> bool:
    """
    Save workspace data to a JSON file.

    Args:
        workspace_id: The identifier for the workspace
        workspace_data: The data to save

    Returns:
        True if the workspace was successfully saved, False otherwise
    """
    ensure_outputs_directory_exists()
    file_path = OUTPUTS_DIRECTORY / f"{workspace_id}.json"

    try:
        with file_path.open("w") as file:
            json.dump(workspace_data, file, indent=2)

        logger.info(f"Workspace data successfully written to file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error writing workspace data to file {file_path}: {str(e)}")
        return False
