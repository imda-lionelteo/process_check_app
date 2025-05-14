import streamlit as st


def click_back_button():
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

    Shows Back, Start Over, and Next buttons as appropriate based on the current section.
    Only displays navigation controls when the user has progressed beyond the triage section.
    The Next button is always displayed for sections 1-4 when appropriate.

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
            st.button(
                "Next →",
                on_click=click_next_button,
                use_container_width=True,
            )


def welcome():
    """
    Display the introduction page for the AI Verify Process Checklist application.

    This function shows information about the testing framework, its benefits,
    target users, and principles covered. It also provides navigation buttons
    to move between sections.
    """
    # Add custom CSS for purple headers
    st.markdown(
        """
        <style>
        h3 {
            color: #4C1D95 !important;  /* Purple color */
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.write(
        """
        ### AI Verify Testing Framework for Generative AI - Process Checks
        This tool helps you assess and document the responsible AI practices that you have
        implemented in deploying your Generative AI application, and generate a summary report. 

        ### How can the Testing Framework and Generated Report help companies?
        - Transparency and Trust: Share the report with your stakeholders to demonstrate responsible AI practices and build trust in your applications

        - Risk Management: Identify potential gaps and take corrective actions to ensure alignment with international standards 
        - Global Alignment: Demonstrate alignment with Singapore's AI Verify testing framework and other international frameworks like US NIST AI Risk Management Framework – Generative AI Profile, and G7 Code of Conduct 
        - Continuous Improvement: Regularly update your validation to ensure ongoing alignment with evolving AI governance regulations

        ### Who should use this tool?
        - **AI Application Owners / Developers** looking to demonstrate and document responsible AI governance practices

        - **Internal Compliance Teams** looking to ensure responsible AI practices have been implemented
        - **External Auditors** looking to validate your clients' implementation of responsible AI practices

        ### About the Testing Framework Process Checks
        The testing framework covers responsible AI practices and measures that are aligned with 11 internationally recognised AI governance principles:
        1. Transparency 
        2. Explainability 
        3. Repeatability / Reproducibility
        4. Safety 
        5. Security 
        6. Robustness
        7. Fairness
        8. Data Governance 
        9. Accountability 
        10. Human Agency and Oversight 
        11. Inclusive Growth, Societal and Environmental Well-being
        
        The processes in the testing framework are mapped to the following international frameworks:
        - Hiroshima Process International Code of Conduct for Organizations Developing Advanced AI Systems (Hiroshima Process CoC)

        - U.S. National Institute of Standards and Technology (NIST) Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile (US NIST AI RMF)

        AI Verify processes that are mapped to these frameworks will have respective labels e.g. "Hiroshima Process CoC" or "US NIST AI RMF" next to them.

        ### Technical Testing for Generative AI Applications
        In the process checks, references were made to conduct technical tests on the Generative AI applications.
        These can be achieved through the use of technical testing tools such as Project Moonshot.

        Only results from the technical tests conducted using Project Moonshot can be uploaded into this tool to be included in the summary report.
        Access Project Moonshot [here](https://github.com/aiverify-foundation).
    """  # noqa: E501, W291, W293
    )

    # Display the navigation buttons
    display_navigation_buttons()
