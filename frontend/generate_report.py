import time  # Import time to simulate progress

import streamlit as st
from backend.actions_components.actions_component import (
    create_actions_component_no_excel,
)
from backend.pdf_generator import GENERATED_REPORT_NAME, generate_pdf_report
from backend.workspace import initialize, load_workspace, save_workspace


def display_generate_report():
    """
    Display the generate report interface.

    This function initializes the session state, displays the report form,
    and shows navigation buttons for the user to interact with.
    """
    # Initialize session state
    initialize_session_state()

    # Display the report form
    display_report_form()

    # Display navigation buttons
    display_navigation_buttons()


def initialize_session_state():
    """
    Initialize the session state for the application.

    Sets up default values for workspace ID, application information, and section
    if they are not already present in the session state.
    """
    if "workspace_id" not in st.session_state:
        initialize(workspace_id="default")

    workspace_data = load_workspace(st.session_state["workspace_id"])
    if "workspace_data" not in st.session_state:
        st.session_state["workspace_data"] = workspace_data

    if "section" not in st.session_state:
        st.session_state["section"] = 1


def render_action_buttons():
    """
    Render action buttons for editing application information.

    Displays buttons for editing application information and handles the
    transition to edit mode if the user chooses to edit.
    """
    workspace_id = st.session_state.get("workspace_id", "")
    company_name = st.session_state["workspace_data"].get("company_name", "")
    app_name = st.session_state["workspace_data"].get("app_name", "")
    app_description = st.session_state["workspace_data"].get("app_description", "")

    if "edit_mode" not in st.session_state:
        st.session_state["edit_mode"] = False

    if not st.session_state["edit_mode"]:
        action = create_actions_component_no_excel(
            workspace_id=workspace_id,
            company_name=company_name,
            app_name=app_name,
            app_description=app_description,
        )

        if action:
            if action == "edit":
                st.session_state["edit_mode"] = True
                st.rerun()
    else:
        display_edit_form()


def display_edit_form():
    """
    Display the form for editing application information.

    Provides input fields for the user to update the company name, application name,
    and application description. Handles saving or canceling the changes.
    """
    current_app_name = st.session_state["workspace_data"].get("app_name", "")
    current_app_description = st.session_state["workspace_data"].get(
        "app_description", ""
    )
    current_company_name = st.session_state["workspace_data"].get("company_name", "")

    with st.form("edit_app_info_form"):
        new_company_name = st.text_input(
            "Company Name",
            key="company_name",
            value=current_company_name,
            help="The name of the company associated with the application.",
            max_chars=100,
        )

        new_app_name = st.text_input(
            "Application Name",
            key="app_name",
            value=current_app_name,
            help=(
                "The name of the application will be reflected in the report generated "
                "after you complete the process checks and technical tests (optional)"
            ),
            max_chars=50,
        )

        new_app_description = st.text_area(
            "Application Description",
            key="app_description",
            value=current_app_description,
            help=(
                "Briefly describe the application being assessed, including its purpose, "
                "key features, and any relevant context. This will help provide a clearer "
                "understanding of the application for your stakeholders reading the report"
            ),
            height=150,
            max_chars=256,
        )

        col1, col2 = st.columns(2)
        with col1:
            save_button = st.form_submit_button(
                "Save Changes", type="primary", use_container_width=True
            )
        with col2:
            cancel_button = st.form_submit_button("Cancel", use_container_width=True)

    if save_button:
        missing_fields = []
        if not new_company_name:
            missing_fields.append("Company Name")
        if not new_app_name:
            missing_fields.append("Application Name")
        if not new_app_description:
            missing_fields.append("Application Description")

        if not missing_fields:
            st.session_state["workspace_data"]["company_name"] = new_company_name
            st.session_state["workspace_data"]["app_name"] = new_app_name
            st.session_state["workspace_data"]["app_description"] = new_app_description
            st.success("App information updated successfully!")
            st.session_state["edit_mode"] = False
            st.session_state["needs_refresh"] = True

            save_workspace(
                st.session_state["workspace_id"], st.session_state["workspace_data"]
            )
            st.rerun()
        else:
            st.error(
                f"Please provide a valid {', '.join(missing_fields)} to proceed with saving changes."
            )

    if cancel_button:
        st.session_state["edit_mode"] = False
        st.rerun()


def display_report_form():
    """
    Display the form for generating the technical report.

    Renders the form with styling, action buttons, and a preview button
    that simulates progress and generates a PDF report.
    """
    st.markdown(
        """
        <style>
        h2 {
            color: #4C1D95 !important;  /* Purple color */
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        .centered-button {
            display: flex;
            justify-content: center;
            margin-top: 20px;
            width: 1000px;
        }
        .stDownloadButton button {
            background-color: #007BFF !important;  /* Bootstrap blue */
            color: white !important;
            width: 100%
        }
        .stProgress > div > div > div > div {
            background-color: #007BFF !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.write("## Generate Your Technical Report")

    # Render action buttons
    render_action_buttons()

    if st.button("Preview Report"):
        # Initialize progress bar
        progress_bar = st.progress(0)

        # Simulate progress
        for percent_complete in range(100):
            time.sleep(0.01)  # Simulate time delay for each step
            progress_bar.progress(percent_complete + 1)

        # Generate the PDF report
        pdf_file_path = generate_pdf_report(st.session_state["workspace_data"])

        # Remove the progress bar after completion
        progress_bar.empty()

        display_pdf_preview(GENERATED_REPORT_NAME)

        # Read the PDF file to prepare for download
        with open(pdf_file_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        st.markdown("<div class='centered-button'>", unsafe_allow_html=True)
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=GENERATED_REPORT_NAME,
            mime="application/pdf",
            use_container_width=False,
            key="download_button",
        )
        st.markdown("</div>", unsafe_allow_html=True)


def display_pdf_preview(pdf_file_path):
    """
    Display a preview of the generated PDF report.

    Embeds the PDF report in an iframe for the user to view before downloading.

    Args:
        pdf_file_path (str): The file path of the PDF to be displayed.
    """
    # Display the PDF viewer with a border
    # pdf_viewer(pdf_file_path, width=800, height=800)
    st.markdown(
        f"""
        <div class="centered-preview" style="width: 100%;">
            <iframe src="http://localhost:8000/temp_report/{pdf_file_path}" width="100%"
            height="800" type="application/pdf"></iframe>
        </div>
    """,
        unsafe_allow_html=True,
    )


def click_back_button() -> None:
    """
    Decrement the 'section' in the session state to navigate to the previous section.

    Returns:
        None
    """
    st.session_state["section"] -= 1


def click_next_button():
    """
    Increment the 'section' in the session state to navigate to the next section.

    Returns:
        None
    """
    st.session_state["section"] += 1


def click_start_over_button() -> None:
    """
    Return to the home page by clearing the session state.

    Displays a confirmation dialog before returning to the home page.
    Progress is automatically saved, so no data will be lost.

    Returns:
        None
    """

    # Using st.dialog as a function decorator
    @st.dialog("Return to Home Page")
    def confirm_reset_dialog() -> None:
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

    Shows Back and Start Over buttons as appropriate based on the current section.
    Only displays navigation controls when the user has progressed beyond the triage section.

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
    with col3:
        if st.session_state["section"] > 1:
            st.button("← Back", on_click=click_back_button, use_container_width=True)
