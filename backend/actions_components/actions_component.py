import os

import streamlit.components.v1 as components


def create_actions_component(
    workspace_id: str,
    app_name: str,
    app_description: str,
):
    """
    Create a Streamlit component for workspace information and action buttons.

    Args:
        workspace_id: The ID of the current workspace
        app_name: The name of the app
        app_description: The description of the app

    Returns:
        str or None: Action to perform if a button was clicked, None otherwise
    """
    # Get component directory and set HTML path
    component_dir = os.path.dirname(__file__)
    actions_html_path = os.path.join(component_dir, "index.html")

    # Generate the HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* Workspace info container styles */
            .workspace-info-container {
                display: flex;
                flex-direction: row;
                border: none;
                border-radius: 0;
                margin-bottom: 16px;
                padding: 0;
                overflow: hidden;
                font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif;
            }
            
            .workspace-info-left {
                flex: 3;
                padding: 20px 24px 20px 0;
                position: relative;
            }
            
            .workspace-info-divider {
                width: 1px;
                background-color: #e5e7eb;
                margin: 0 12px;
            }
            
            .workspace-info-field {
                font-size: 12px;
                color: #6b7280;
                font-weight: 500;
                margin-bottom: 6px;
                letter-spacing: 0.025em;
            }
            
            .workspace-info-value {
                font-size: 15px;
                font-weight: 400;
                color: #111827;
                line-height: 1.5;
                margin-bottom: 16px;
                display: block;
            }
            
            .workspace-info-description {
                display: block;
                font-size: 16px;
                color: #4b5563;
                margin-bottom: 18px;
                line-height: 1.5;
                margin-top: 4px;
            }
            
            .workspace-info-field.workspace-id-field {
                font-size: 14px;
                color: #4b5563;
                font-weight: 600;
                margin-top: 16px;
                margin-bottom: 8px;
                display: block;
            }
            
            .workspace-id-tag {
                display: inline-block;
                font-size: 14px;
                padding: 5px 10px;
                background-color: #f0f4f8;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                color: #1f2937;
                font-family: 'Roboto Mono', monospace;
                letter-spacing: 0.025em;
                font-weight: 500;
            }
            
            .edit-btn {
                position: absolute;
                top: 16px;
                right: 16px;
                background-color: transparent;
                border: none;
                width: 32px;
                height: 32px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                color: #6b7280;
                transition: all 0.2s;
            }
            
            .edit-btn:hover {
                background-color: #f3f4f6;
                color: #374151;
            }
            
            .material-icon {
                font-size: 16px;
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    </head>
    <body>
        <div id="actions-container">
            <div class="workspace-info-container">
                <div class="workspace-info-left" style="width: 400px;">
                    <div style="width: 100%; overflow: hidden;">
                        <div class="workspace-info-field">Application Name</div>
                        <span class="workspace-info-value" id="app-name" style="display: block; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;"></span>
                    </div>
                    <div style="width: 100%; overflow: hidden;">
                        <div class="workspace-info-field">Application Description</div>
                        <span class="workspace-info-description" id="app-description" style="display: block; white-space: pre-wrap; word-wrap: break-word;"></span>
                    </div>
                    <div style="margin-top: 16px; width: 100%; overflow: hidden;">
                        <div class="workspace-info-field workspace-id-field">Workspace ID</div>
                        <span class="workspace-id-tag" id="workspace-id" style="display: inline-block; max-width: 100%; text-overflow: ellipsis; overflow: hidden;"></span>
                    </div>
                    <button class="edit-btn" id="edit-button">
                        <span class="material-symbols-rounded material-icon">edit</span>
                    </button>
                </div>
                <div class="workspace-info-divider"></div>
            </div>
        </div>
        
        <script>
            // Function to send messages to Streamlit
            function sendMessageToStreamlit(type, data) {
                const outData = Object.assign({
                    isStreamlitMessage: true,
                    type: type,
                }, data);
                window.parent.postMessage(outData, "*");
            }
            
            // Initialize component
            function init() {
                sendMessageToStreamlit("streamlit:componentReady", {apiVersion: 1});
            }
            
            // Set the frame height
            function setFrameHeight(height) {
                sendMessageToStreamlit("streamlit:setFrameHeight", {height: height});
            }
            
            // Send data to Python when buttons are clicked
            function sendDataToPython(action) {
                sendMessageToStreamlit("streamlit:setComponentValue", {
                    value: action,
                    dataType: "json",
                });
            }
            
            // Handle clicks on buttons
            document.getElementById('edit-button').addEventListener('click', function() {
                sendDataToPython('edit');
            });
            
            // Handle data from Python
            function onDataFromPython(event) {
                if (event.data.type !== "streamlit:render") return;
                
                const data = event.data.args;
                if (!data) return;
                
                // Update UI elements with data from Python
                const workspaceId = data.workspace_id || "";
                const appName = data.app_name || "";
                const appDescription = data.app_description || "";
                
                document.getElementById('workspace-id').innerHTML = workspaceId || '<span style="color:#9ca3af;">No workspace ID provided.</span>';
                document.getElementById('app-name').innerHTML = appName || '<span style="color:#9ca3af;">No application name provided.</span>';
                document.getElementById('app-description').innerHTML = appDescription || '<span style="color:#9ca3af;">No description provided.</span>';
                
                // Calculate dynamic height based on content
                calculateAndSetHeight();
            }
            
            // Function to dynamically calculate height
            function calculateAndSetHeight() {
                const container = document.getElementById('actions-container');
                const containerHeight = container.getBoundingClientRect().height;
                
                // Apply min, max constraints with padding
                const finalHeight = Math.min(Math.max(containerHeight + 20, 180), 450);
                setFrameHeight(finalHeight);
            }
            
            // Event listeners
            window.addEventListener("message", onDataFromPython);
            window.addEventListener("load", () => setTimeout(calculateAndSetHeight, 100));
            window.addEventListener("resize", calculateAndSetHeight);
            
            // Initialize the component
            init();
        </script>
    </body>
    </html>
    """  # noqa: E501, W291, W293

    # Write the HTML to file
    with open(actions_html_path, "w") as f:
        f.write(html_content)

    # Create and return the component
    component = components.declare_component("actions_component", path=component_dir)
    return component(
        workspace_id=workspace_id,
        app_name=app_name,
        app_description=app_description,
        key="actions_component",
    )


def create_actions_component_no_excel(
    workspace_id: str,
    company_name: str,
    app_name: str,
    app_description: str,
):
    """
    Create a Streamlit component for workspace information and action buttons.

    Args:
        workspace_id: The ID of the current workspace
        company_name: The name of the company
        app_name: The name of the app
        app_description: The description of the app

    Returns:
        str or None: Action to perform if a button was clicked, None otherwise
    """
    # Create component directory
    component_dir = os.path.dirname(__file__)

    # Set the path for actions_component.html directly in the current directory
    actions_html_path = os.path.join(component_dir, "index.html")

    # Generate the HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* Workspace info container styles */
            .workspace-info-container {
                display: flex;
                flex-direction: row;
                border: none;
                border-radius: 0;
                margin-bottom: 16px;
                padding: 0;
                overflow: hidden;
                font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif;
            }
            
            .workspace-info-left {
                flex: 3;
                padding: 20px 24px 20px 0;
                position: relative;
            }
            
            .workspace-info-right {
                flex: 1;
                padding: 20px 0 20px 24px;
                background-color: #ffffff;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 16px;
            }
            
            .workspace-info-divider {
                width: 1px;
                background-color: #e5e7eb;
                margin: 0 12px;
            }
            
            .workspace-info-field {
                font-size: 12px;
                color: #6b7280;
                font-weight: 500;
                margin-bottom: 6px;
                letter-spacing: 0.025em;
            }
            
            .workspace-info-value {
                font-size: 15px;
                font-weight: 600;
                color: #111827;
                line-height: 1.5;
                margin-bottom: 16px;
                display: block;
            }
            
            .workspace-info-description {
                display: block;
                font-size: 16px;
                color: #4b5563;
                margin-bottom: 18px;
                line-height: 1.5;
                margin-top: 4px;
            }
            
            .workspace-info-field.workspace-id-field {
                font-size: 14px;
                color: #4b5563;
                font-weight: 600;
                margin-top: 16px;
                margin-bottom: 8px;
                display: block;
            }
            
            .workspace-id-tag {
                display: inline-block;
                font-size: 14px;
                padding: 5px 10px;
                background-color: #f0f4f8;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                color: #1f2937;
                font-family: 'Roboto Mono', monospace;
                letter-spacing: 0.025em;
                font-weight: 500;
            }
            
            .autosave-indicator {
                color: #10b981;
                font-size: 13px;
                font-weight: 500;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 10px;
            }
            
            .edit-btn {
                position: absolute;
                top: 16px;
                right: 16px;
                background-color: transparent;
                border: none;
                width: 32px;
                height: 32px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                color: #6b7280;
                transition: all 0.2s;
            }
            
            .edit-btn:hover {
                background-color: #f3f4f6;
                color: #374151;
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    </head>
    <body>
        <div id="actions-container">
            <div class="workspace-info-container">
                <div class="workspace-info-left">
                    <div>
                        <div class="workspace-info-field">Company Name</div>
                        <span class="workspace-info-value" id="company-name"></span>
                    </div>
                    <div>
                        <div class="workspace-info-field">Application Name</div>
                        <span class="workspace-info-value" id="app-name"></span>
                    </div>
                    <div>
                        <div class="workspace-info-field">Application Description</div>
                        <span class="workspace-info-description" id="app-description"></span>
                    </div>
                    <div style="margin-top: 16px;">
                        <div class="workspace-info-field workspace-id-field">Workspace ID</div>
                        <span class="workspace-id-tag" id="workspace-id"></span>
                    </div>
                    <button class="edit-btn" id="edit-button">
                        <span class="material-symbols-rounded material-icon">edit</span>
                    </button>
                </div>
            </div>
        </div>
        
        <script>
            // Function to send messages to Streamlit
            function sendMessageToStreamlit(type, data) {
                const outData = Object.assign({
                    isStreamlitMessage: true,
                    type: type,
                }, data);
                window.parent.postMessage(outData, "*");
            }
            
            // Initialize component
            function init() {
                sendMessageToStreamlit("streamlit:componentReady", {apiVersion: 1});
            }
            
            // Set the frame height
            function setFrameHeight(height) {
                sendMessageToStreamlit("streamlit:setFrameHeight", {height: height});
            }
            
            // Send data to Python when buttons are clicked
            function sendDataToPython(action) {
                sendMessageToStreamlit("streamlit:setComponentValue", {
                    value: action,
                    dataType: "json",
                });
            }
            
            // Handle clicks on buttons
            document.getElementById('edit-button').addEventListener('click', function() {
                sendDataToPython('edit');
            });
            
            // Handle data from Python
            function onDataFromPython(event) {
                if (event.data.type !== "streamlit:render") return;
                
                const data = event.data.args;
                if (!data) return;
                
                // Update UI elements with data from Python
                const workspaceId = data.workspace_id || "";
                const companyName = data.company_name || "";
                const appName = data.app_name || "";
                const appDescription = data.app_description || "";
                
                document.getElementById('workspace-id').innerHTML = workspaceId || '<span style="color:#9ca3af;">No workspace ID provided.</span>';
                document.getElementById('company-name').innerHTML = companyName || '<span style="color:#9ca3af;">No company name provided.</span>';
                document.getElementById('app-name').innerHTML = appName || '<span style="color:#9ca3af;">No application name provided.</span>';
                document.getElementById('app-description').innerHTML = appDescription || '<span style="color:#9ca3af;">No description provided.</span>';
                
                // Calculate dynamic height based on content
                calculateAndSetHeight();
            }
            
            // Function to dynamically calculate height
            function calculateAndSetHeight() {
                // Get the actual height of the container
                const container = document.getElementById('actions-container');
                const containerHeight = container.getBoundingClientRect().height;
                
                // Set a minimum height to prevent it from being too small
                const minHeight = 180;
                // Respect the max height of 450
                const maxHeight = 450;
                
                // Add some padding to ensure content is fully visible
                const heightWithPadding = containerHeight + 20;
                
                // Apply min, max constraints
                const finalHeight = Math.min(Math.max(heightWithPadding, minHeight), maxHeight);
                
                // Set the height
                setFrameHeight(finalHeight);
            }
            
            // Event listeners
            window.addEventListener("message", onDataFromPython);
            window.addEventListener("load", function() {
                // Initial height calculation after DOM content is loaded
                setTimeout(calculateAndSetHeight, 100);
            });
            
            // Also recalculate on window resize
            window.addEventListener("resize", function() {
                calculateAndSetHeight();
            });
            
            // Initialize the component
            init();
        </script>
    </body>
    </html>
    """  # noqa: E501, W291, W293

    # Write the HTML to file directly in the current directory
    with open(actions_html_path, "w") as f:
        f.write(html_content)

    # Create and return the component
    component = components.declare_component("actions_component", path=component_dir)

    # Return the instantiated component with updated data
    return component(
        workspace_id=workspace_id,
        company_name=company_name,
        app_name=app_name,
        app_description=app_description,
        key="actions_component",
    )
