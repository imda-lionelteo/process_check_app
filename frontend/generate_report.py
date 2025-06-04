import streamlit as st
from backend.actions_components.actions_component import (
    create_actions_component_no_excel,
)
from backend.pdf_generator import GENERATED_REPORT_NAME, generate_pdf_report
from backend.workspace import initialize, load_workspace, save_workspace


def display_generate_report():
    """
    Main entry point for the report generation interface.
    Initializes session state, displays the report form, and navigation buttons.
    """
    initialize_session_state()
    display_report_form()
    display_navigation_buttons()


def initialize_session_state():
    """
    Ensure required session state variables are initialized.
    """
    if "workspace_id" not in st.session_state:
        initialize(workspace_id="default")
    if "workspace_data" not in st.session_state:
        st.session_state["workspace_data"] = load_workspace(
            st.session_state["workspace_id"]
        )
    if "section" not in st.session_state:
        st.session_state["section"] = 1


def render_action_buttons():
    """
    Render action buttons for editing application information.
    Handles transition to edit mode if user chooses to edit.
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
        if action == "edit":
            st.session_state["edit_mode"] = True
            st.rerun()
    else:
        display_edit_form()


def display_edit_form():
    """
    Display a form for editing application information.
    Handles saving or canceling changes.
    """
    current_data = st.session_state["workspace_data"]
    with st.form("edit_app_info_form"):
        new_company_name = st.text_input(
            "Company Name",
            key="company_name",
            value=current_data.get("company_name", ""),
            help="The name of the company associated with the application.",
            max_chars=100,
        )
        new_app_name = st.text_input(
            "Application Name",
            key="app_name",
            value=current_data.get("app_name", ""),
            help=(
                "The name of the application will be reflected in the report generated "
                "after you complete the process checks and technical tests (optional)"
            ),
            max_chars=50,
        )
        new_app_description = st.text_area(
            "Application Description",
            key="app_description",
            value=current_data.get("app_description", ""),
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
            current_data["company_name"] = new_company_name
            current_data["app_name"] = new_app_name
            current_data["app_description"] = new_app_description
            st.success("App information updated successfully!")
            st.session_state["edit_mode"] = False
            st.session_state["needs_refresh"] = True
            save_workspace(st.session_state["workspace_id"], current_data)
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
    Display the form for generating the report.
    Renders action buttons and a button to generate and preview the PDF report.
    """
    st.markdown(
        """
        <style>
        h2 { color: #4C1D95 !important; margin-top: 1.5rem; margin-bottom: 1rem; }
        .centered-button { display: flex; justify-content: center; margin-top: 20px; width: 100%; }
        .stProgress > div > div > div > div { background-color: #007BFF !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.write("## Generate Your Report")
    render_action_buttons()

    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating your report..."):
            pdf_file_path = generate_pdf_report(st.session_state["workspace_data"])
            st.markdown("---")
            st.markdown("#### Preview Your Report")
            display_pdf_preview(GENERATED_REPORT_NAME)

            with open(pdf_file_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=GENERATED_REPORT_NAME,
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_button",
                    type="primary",
                )

            st.markdown(
                "<div style='text-align: center; color: #4C1D95; font-size: 1.2em; margin: 20px 0;'>"
                "You’ve reached the end of the tool.<br><br>"
                "To start a new process checks, click Home. Otherwise, you may safely close this window.<br><br>"
                "We encourage you to share your report with stakeholders to demonstrate responsible AI practices and build trust in your applications. We also welcome your feedback and experiences with this framework and tool — please share them with us at info@aiverify.sg"  # noqa: E501
                "</div>",
                unsafe_allow_html=True,
            )


def display_pdf_preview(pdf_file_path):
    """
    Display a preview of the generated PDF report in an iframe.
    Args:
        pdf_file_path (str): The file path of the PDF to be displayed.
    """
    st.markdown(
        f"""
        <div class="centered-preview" style="width: 100%;">
            <iframe src="http://localhost:8000/temp_report/{pdf_file_path}" width="100%" height="800" type="application/pdf"></iframe>
        </div>
        """,  # noqa: E501
        unsafe_allow_html=True,
    )


def click_back_button():
    """Navigate to the previous section."""
    st.session_state["section"] -= 1


def click_start_over_button():
    """
    Show a confirmation dialog to return to the home page and clear session state.
    """

    @st.dialog("Return to Home Page")
    def confirm_reset_dialog():
        st.write(
            "Do you want to return to Home Page? Don't worry, your progress has been saved."
        )
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Yes, start over", use_container_width=True):
                server_started = st.session_state.get("server_started", False)
                st.session_state.clear()
                st.session_state["server_started"] = server_started
                st.rerun()

        with col2:
            if st.button("No, cancel", use_container_width=True):
                st.rerun()

    # Call the dialog function to display it
    confirm_reset_dialog()


def display_navigation_buttons():
    """
    Display navigation buttons for moving between sections of the process checks.
    Shows Back and Start Over buttons as appropriate.
    """
    if st.session_state["section"] >= 1:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("---")
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
