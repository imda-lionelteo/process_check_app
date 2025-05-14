import base64
import json
import os
import tempfile

import streamlit as st
from backend.report_validation import validate_json
from backend.workspace import initialize, save_workspace

SAMPLE_REPORT_PATH = "assets/sample_report.json"


def click_back_button() -> None:
    """
    Navigate to the previous section by decrementing the 'section' in the session state.

    This function decreases the current section index in the session state,
    allowing the user to move back to the previous section in the process checks.

    Returns:
        None
    """
    st.session_state["section"] -= 1


def click_next_button():
    """
    Navigate to the next section by incrementing the 'section' in the session state.

    This function increases the current section index in the session state,
    allowing the user to proceed to the next section in the process checks.

    Returns:
        None
    """
    st.session_state["section"] += 1


def click_start_over_button() -> None:
    """
    Return to the home page by clearing the session state.

    This function displays a confirmation dialog before clearing the session state
    and returning to the home page. Progress is automatically saved, so no data will be lost.

    Returns:
        None
    """

    # Using st.dialog as a function decorator
    @st.dialog("Return to Home Page")
    def confirm_reset_dialog() -> None:
        """
        Display a confirmation dialog for returning to the home page.

        This dialog asks the user if they want to return to the home page,
        reassuring them that their progress has been saved.

        Returns:
            None
        """
        st.write(
            "Do you want to return to Home Page? Don't worry, your progress has been saved."
        )
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Yes, start over", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        with col2:
            if st.button("No, cancel", use_container_width=True):
                st.rerun()

    # Call the dialog function to display it
    confirm_reset_dialog()


def display_navigation_buttons() -> None:
    """
    Display navigation buttons for moving between sections of the process checks.

    This function shows Back, Home, and Next buttons as appropriate based on the current section.
    Only displays navigation controls when the user has progressed beyond the triage section.
    The Next button is disabled if not all questions are answered.

    Returns:
        None
    """
    if st.session_state["section"] >= 1:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("---")

    # Regular navigation buttons
    col1, _, col2, col3 = st.columns([2, 6, 2, 2])
    with col1:
        if st.session_state["section"] >= 1:
            st.button(
                ":material/home: Home",
                on_click=click_start_over_button,
                use_container_width=True,
            )
    with col2:
        if st.session_state["section"] > 1:
            st.button("← Back", on_click=click_back_button, use_container_width=True)
    with col3:
        # Display the Next button for sections 1-4
        if st.session_state["section"] < 5 and st.session_state["section"] >= 1:
            # Get progress data from session state
            progress_data = st.session_state["workspace_data"].get("progress_data", {})
            total_questions = progress_data.get("total_questions", 0)
            total_answered = progress_data.get("total_answered_questions", 0)
            # Disable Next if not all questions are answered

            st.button(
                "Next →",
                on_click=click_next_button,
                use_container_width=True,
                disabled=(total_answered != total_questions),
                help=(
                    "Please answer all questions before proceeding."
                    if total_answered != total_questions
                    else None
                ),
            )


def apply_custom_styles():
    """
    Apply custom CSS styles for the upload result page.

    This function sets up styling for fonts, containers, headers, buttons, and dividers
    to create a consistent and visually appealing user interface.

    Returns:
        None
    """
    st.markdown(
        """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@600;700;800&display=swap');  # noqa: E501
        /* Main container styling */
        .stApp {
            background-color: #f9fafb;
            font-family: 'Inter', sans-serif;
        }
        /* Header styling */
        h2 {
            color: #4C1D95 !important;  /* Purple color */
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        /* Subtitle styling */
        .subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1.2rem;
            text-align: center;
            color: #4b5563; /* Gray */
            margin-bottom: 1.5rem;
            font-weight: 500;
            letter-spacing: -0.2px;
        }
        /* Divider styling */
        .custom-divider {
            display: flex;
            align-items: center;
            text-align: center;
            color: #6b7280; /* Gray */
            font-size: 1.1rem;
            margin: 3rem 0;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
        }
        .custom-divider::before,
        .custom-divider::after {
            content: '';
            flex: 1;
            border-bottom: 2px solid #e5e7eb; /* Light gray */
        }
        .custom-divider span {
            margin: 0 1rem;
            font-weight: 500;
        }
        /* JSON preview styling */
        .json-preview {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #e5e7eb; /* Light gray */
            padding: 10px;
            background-color: #f9fafb; /* Very light gray */
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def display_json_content(file_path):
    """
    Display JSON content from a given file path.

    This function reads a JSON file from the specified file path,
    formats it with indentation, and displays it in a scrollable div
    on the Streamlit app.

    Args:
        file_path (str): The path to the JSON file to be displayed.

    Returns:
        None
    """
    with open(file_path, "r") as f:
        data = json.load(f)
        json_str = json.dumps(data, indent=4)
        st.markdown(
            f'<div class="json-preview">{json_str}</div>', unsafe_allow_html=True
        )


def upload_result():
    """
    Handle the upload and display of technical test results.

    This function manages the upload of JSON files containing technical test results
    from Project Moonshot. It validates the uploaded file, displays its content,
    and provides options for downloading sample JSON files if no test results are available.

    Returns:
        None
    """
    apply_custom_styles()

    st.write(
        """
        ## Upload Technical Test Results (Optional)
    """
    )

    st.write(
        "If you do not have any technical test results from Project "
        "Moonshot, you can skip this step without concern. The generated "
        "report will still provide valuable insights based on the process "
        "checks that you have completed."
    )

    # Initialize the workspace if not already done
    if "workspace_id" not in st.session_state:
        initialize(workspace_id="default")

    # Ensure "workspace_data" is initialized
    if "workspace_data" not in st.session_state:
        st.session_state["workspace_data"] = {}

    # Ensure "upload_results" is initialized
    if "upload_results" not in st.session_state["workspace_data"]:
        st.session_state["workspace_data"]["upload_results"] = {}

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # File uploader for JSON files with optional indication
    uploaded_file = st.file_uploader(
        # label="Upload your JSON file",
        type=["json"],
        label=(
            "If you wish to include results from previous technical tests "
            "conducted using Project Moonshot in this report, you can upload "
            "the JSON file (1 file only) below:"
        ),
        accept_multiple_files=False,  # Ensure only one file can be uploaded
    )

    # Display the previously uploaded file only once when the page is loaded
    if "file_path" in st.session_state["workspace_data"]["upload_results"]:
        previous_file_path = st.session_state["workspace_data"]["upload_results"][
            "file_path"
        ]
        # Check if the file still exists
        if os.path.exists(previous_file_path):
            file_name = os.path.basename(previous_file_path)
            if "file_displayed" not in st.session_state:
                st.info(
                    f"You previously uploaded {file_name}. You can use the 'Browse file' button to replace your current file."  # noqa: E501
                )
                display_json_content(previous_file_path)
                st.session_state["file_displayed"] = True
        else:
            # Remove the file path if the file does not exist
            del st.session_state["workspace_data"]["upload_results"]["file_path"]

    if uploaded_file is not None:
        # Save the uploaded file to the temporary directory
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Read the JSON content
        with open(file_path, "r") as f:
            data = json.load(f)
            # Validate the JSON schema using the imported function
            if validate_json(data):
                st.success("File uploaded successfully")
                # Convert JSON to a formatted string
                json_str = json.dumps(data, indent=4)
                # Display the JSON content in a scrollable div
                st.markdown(
                    f'<div class="json-preview">{json_str}</div>',
                    unsafe_allow_html=True,
                )

                # Update the session state with the new file path
                st.session_state["workspace_data"]["upload_results"][
                    "file_path"
                ] = file_path
                # Save the session state to the workspace
                workspace_id = st.session_state["workspace_id"]
                save_workspace(workspace_id, st.session_state["workspace_data"])

                # Clear the previous file display flag
                st.session_state["file_displayed"] = False
            else:
                st.error(
                    "The file you uploaded isn’t in the correct format. Please upload a valid Project Moonshot JSON file."  # noqa: E501
                )
                # Optionally, delete the file if the schema is invalid
                os.remove(file_path)

    # Section for users without a test result
    st.markdown("---")

    st.write(
        """
        ## Don’t have Project Moonshot technical test results?
    """
    )
    st.write("You can download the sample Project Moonshot JSON files below:")

    # Helper function to create a download link
    def get_download_link(data: str, filename: str, link_text: str):
        """
        Create a download link for a given data string.

        This function encodes the provided data string in base64 format
        and generates an HTML link for downloading the data as a file.

        Args:
            data (str): The data to be encoded and downloaded.
            filename (str): The name of the file to be downloaded.
            link_text (str): The text to display for the download link.

        Returns:
            str: An HTML string for the download link.
        """
        b64 = base64.b64encode(data.encode()).decode()
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}">{link_text}</a>'
        return href

    with open(SAMPLE_REPORT_PATH, "r") as sample_file:
        sample_data = sample_file.read()
        download_link_1 = get_download_link(sample_data, "sample_report.json", "here")
        download_link_2 = get_download_link(sample_data, "sample_report.json", "here")

    st.markdown(
        f"""
        - If you are using Moonshot version 1.0, you can download the sample result {download_link_1}.
        - If you are using Moonshot version 0.6.3, you can download the sample result {download_link_2}.
        """,
        unsafe_allow_html=True,
    )

    st.write(
        "If you are keen to find out more about Project Moonshot, click [here](https://github.com/aiverify-foundation)."  # noqa: E501
    )

    # Display the navigation buttons
    display_navigation_buttons()
