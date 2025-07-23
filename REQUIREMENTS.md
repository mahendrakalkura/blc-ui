# Web-Based Broken Link Checker Project

## Project Overview
Create a web application that serves as a frontend for the `broken-link-checker` (blc) Node.js module (version 0.7.8). The app allows users to input a URL, configure scanning options via a user-friendly interface, and view real-time results of broken links, missing images, and other issues in HTML documents. The project combines Python for the backend, HTML/JavaScript for the frontend, and integrates with the `blc` Node.js module to perform link checking.

## Objectives
- Build a web interface with toggles and inputs for all `blc` command-line options.
- Stream scan results (e.g., broken links, errors) to the browser in real-time.
- Provide a beginner-friendly project that reinforces Python, HTML, and JavaScript skills.
- Teach integration between a Node.js module and a Python backend.

## Features
1. **URL Input**: A text field for users to enter the URL of the HTML document to scan.
2. **Configuration Toggles**:
   - Checkboxes for options like `--exclude-external`, `--exclude-internal`, `--follow`, `--get`, `--ordered`, `--recursive`, `--verbose`.
   - A dropdown for `--filter-level` (0, 1, 2, 3).
   - A text input for `--exclude` keywords (support multiple entries).
   - Numeric inputs for `--host-requests` and `--requests` to set concurrent request limits.
   - A text input for `--user-agent` to customize the user agent string.
3. **Real-Time Output**: A section that displays scan results (e.g., broken links, status codes) as they are processed, updating dynamically.
4. **Start/Stop Controls**: Buttons to initiate the scan and stop it if needed.
5. **Clear Feedback**: Display success, error, or excluded link messages, with verbose mode support.

## Technical Requirements
- **Backend**:
  - Use Python with `Flask` or `FastAPI` to create a web server.
  - Use the `subprocess` module or a library like `node-python` to execute `blc` commands and capture output.
  - Implement WebSocket or Server-Sent Events (SSE) for streaming results to the frontend in real-time.
- **Frontend**:
  - Create an HTML page with a form for URL input and configuration options.
  - Use JavaScript to handle user inputs, send requests to the backend, and update the UI with streaming results.
  - Style with basic CSS or a framework like Bootstrap for a clean look.
- **Node.js Integration**:
  - Ensure `broken-link-checker` (v0.7.8) is installed (`npm install broken-link-checker`).
  - Call `blc` commands from Python, passing user-selected options as arguments.
- **Dependencies**:
  - Python: Flask/FastAPI, `websockets` or `sse-starlette` (for streaming).
  - Node.js: `broken-link-checker` module.
  - Frontend: Basic HTML/CSS/JavaScript (optional: Bootstrap CDN for styling).

## Suggested Steps
1. **Set Up the Backend**:
   - Install Python and Node.js.
   - Create a Flask/FastAPI app with an endpoint to receive URL and options.
   - Use `subprocess.run` or `child_process` to execute `blc` with the provided options.
   - Implement SSE or WebSocket to stream `blc` output to the frontend.
2. **Build the Frontend**:
   - Create an HTML form with:
     - Text input for the URL.
     - Checkboxes for boolean options (`--exclude-external`, `--exclude-internal`, etc.).
     - Dropdown for `--filter-level` (0–3).
     - Text input for `--exclude` (comma-separated for multiple keywords).
     - Numeric inputs for `--host-requests` and `--requests`.
     - Text input for `--user-agent`.
     - "Start Scan" and "Stop Scan" buttons.
   - Use JavaScript to collect form data and send it to the backend via a POST request.
   - Display streaming results in a `<div>` or `<pre>` element, updating as new data arrives.
3. **Integrate and Stream**:
   - Parse `blc` output (e.g., JSON or text) in the backend.
   - Send results incrementally to the frontend using SSE/WebSocket.
   - Ensure the UI updates smoothly with each result (e.g., link URL, status, error message).
4. **Test and Refine**:
   - Test with sample URLs (e.g., `http://example.com`).
   - Verify all `blc` options work as expected.
   - Ensure real-time updates are smooth and stop button cancels the scan.
5. **Polish the UI**:
   - Add basic CSS or Bootstrap for a clean layout.
   - Provide visual feedback (e.g., loading spinner, success/error colors).

## Learning Outcomes
- **Python**: Learn to build a web server, handle subprocesses, and stream data.
- **HTML/JavaScript**: Create interactive forms, handle events, and update the DOM dynamically.
- **Node.js Integration**: Understand how to interface Python with Node.js modules.
- **Real-Time Web**: Gain experience with SSE or WebSocket for live updates.
- **Problem-Solving**: Debug issues with `blc` output parsing and UI responsiveness.

## Example Workflow
1. User enters a URL (e.g., `http://example.com`) and selects options (e.g., `--recursive`, `--filter-level 2`).
2. User clicks "Start Scan."
3. Frontend sends data to the Python backend.
4. Backend constructs and runs the `blc` command (e.g., `blc http://example.com -r --filter-level 2`).
5. Backend streams results (e.g., "Link: /page1 - Status: 404") to the frontend.
6. Frontend displays results in real-time, updating the UI as new links are checked.
7. User can stop the scan, and the UI reflects the cancellation.

## Stretch Goals
- Add a "Save Results" button to download the scan output as a text file.
- Highlight broken links in red and valid links in green.
- Support multiple URLs in a single scan session.
- Add a progress bar for recursive scans.

## Resources
- `broken-link-checker` Documentation: [npmjs.com/package/broken-link-checker](https://www.npmjs.com/package/broken-link-checker)
- Flask SSE Example: [flask-sse.readthedocs.io](https://flask-sse.readthedocs.io)
- FastAPI WebSocket: [fastapi.tiangolo.com/advanced/websockets](https://fastapi.tiangolo.com/advanced/websockets)
- Bootstrap CDN: [getbootstrap.com](https://getbootstrap.com)

This project is a great way to combine your Python and HTML/JavaScript skills while building something practical and fun! Let me know if you need help setting up any part of it.