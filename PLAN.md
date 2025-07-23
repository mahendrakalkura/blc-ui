# Complete Guide to Building a Web-Based Broken Link Checker

This guide provides a step-by-step walkthrough for building a web application that serves as a frontend for the `broken-link-checker` (blc) Node.js module (version 0.7.8). The app allows users to input a URL, configure scanning options via a user-friendly interface, and view broken link results in real-time. It uses Python (FastAPI) for the backend, HTML/JavaScript for the frontend, and integrates with the `blc` module. This guide assumes you know basic Python (variables, functions, lists) and HTML/JavaScript (creating elements, handling events), but no prior experience with web servers or Node.js is required.

## Project Overview
The application will:
- Provide a web form with inputs for a URL and all `blc` options (e.g., `--recursive`, `--filter-level`).
- Send user inputs to a Python backend that runs the `blc` command.
- Stream results (e.g., broken links, status codes) to the browser in real-time using Server-Sent Events (SSE).
- Display results dynamically with a clean interface styled using Bootstrap.

## Features
- **URL Input**: A text field for the URL to scan (e.g., `https://example.com`).
- **Configuration Options**:
  - Text input for `--exclude` keywords (comma-separated).
  - Checkboxes for `--exclude-external`, `--exclude-internal`, `--follow`, `--get`, `--ordered`, `--recursive`, `--verbose`.
  - Dropdown for `--filter-level` (0: clickable links, 1: media/iframes, 2: stylesheets/scripts, 3: metadata).
  - Numeric inputs for `--requests` and `--host-requests`.
  - Text input for `--user-agent`.
- **Real-Time Output**: Display scan results (link URL, status, errors) as they are processed.
- **Start/Stop Controls**: Buttons to start and stop the scan.
- **Feedback**: Color-coded results (e.g., errors in red, completion in green).

## Prerequisites
You'll need:
- A computer with internet access.
- A code editor (e.g., VS Code, Notepad++).
- A terminal (Command Prompt on Windows, Terminal on macOS/Linux).
- Python 3.8+ and Node.js installed.

## Step 1: Set Up Your Environment
1. **Install Python**:
   - Download Python 3.8+ from [python.org](https://www.python.org/downloads).
   - Install, ensuring "Add Python to PATH" is checked.
   - Verify in terminal:
     ```
     python --version
     ```
     Expect output like `Python 3.10.0`.
2. **Install Node.js**:
   - Download the LTS version from [nodejs.org](https://nodejs.org).
   - Install and verify:
     ```
     node --version
     npm --version
     ```
     Expect outputs like `v16.13.0` and `8.1.0`.
3. **Create a Project Folder**:
   - Create a folder named `broken-link-checker-web`.
   - Open it in your code editor.
   - In terminal, navigate to it:
     ```
     cd path/to/broken-link-checker-web
     ```
4. **Install `broken-link-checker`**:
   - Run:
     ```
     npm install broken-link-checker@0.7.8
     ```
     This creates a `node_modules` folder and `package.json`.
5. **Install Python Dependencies**:
   - Install FastAPI, Uvicorn, and SSE support:
     ```
     pip install fastapi uvicorn sse-starlette
     ```
   - Verify:
     ```
     pip show fastapi
     ```

## Step 2: Project Structure
Create the following structure in `broken-link-checker-web`:
```
broken-link-checker-web/
├── static/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── app.py
└── package.json
```
- `static/`: Contains frontend files (HTML, CSS, JavaScript).
- `app.py`: Python backend with FastAPI.
- `package.json`: Tracks Node.js dependencies (created by `npm install`).

## Step 3: Backend Implementation (`app.py`)
The backend will:
- Serve the web interface.
- Accept form data (URL and options).
- Run `blc` commands using Node.js.
- Stream results to the frontend using SSE.

**Code for `app.py`**:
```python
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
import subprocess
import asyncio
import json
import shlex

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the main page
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r") as f:
        return f.read()

# Endpoint to start the scan
@app.post("/scan")
async def scan(
    url: str = Form(...),
    exclude: str = Form(""),
    exclude_external: bool = Form(False),
    exclude_internal: bool = Form(False),
    filter_level: int = Form(1),
    follow: bool = Form(False),
    get: bool = Form(False),
    ordered: bool = Form(False),
    recursive: bool = Form(False),
    requests: int = Form(10),
    host_requests: int = Form(5),
    user_agent: str = Form("Mozilla/5.0"),
    verbose: bool = Form(False)
):
    async def event_generator():
        # Build the blc command
        cmd = ["npx", "blc", url, "--filter-level", str(filter_level), "--requests", str(requests), "--host-requests", str(host_requests)]
        if exclude:
            for ex in exclude.split(","):
                if ex.strip():
                    cmd.extend(["--exclude", ex.strip()])
        if exclude_external:
            cmd.append("--exclude-external")
        if exclude_internal:
            cmd.append("--exclude-internal")
        if follow:
            cmd.append("--follow")
        if get:
            cmd.append("--get")
        if ordered:
            cmd.append("--ordered")
        if recursive:
            cmd.append("--recursive")
        if verbose:
            cmd.append("--verbose")
        if user_agent:
            cmd.extend(["--user-agent", user_agent])

        try:
            # Run the command and capture output
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Stream stdout
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_str = line.decode().strip()
                # Try to parse as JSON for structured output
                try:
                    data = json.loads(line_str)
                    yield {
                        "event": "result",
                        "data": json.dumps({
                            "url": data.get("url", ""),
                            "broken": data.get("broken", False),
                            "status": data.get("http", {}).get("status", ""),
                            "reason": data.get("brokenReason", "")
                        })
                    }
                except json.JSONDecodeError:
                    # Fallback for non-JSON output
                    yield {"event": "result", "data": line_str}

            # Stream stderr (errors)
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                yield {"event": "error", "data": line.decode().strip()}

            # Signal completion
            yield {"event": "complete", "data": "Scan completed"}
        except Exception as e:
            yield {"event": "error", "data": f"Server error: {str(e)}"}

    return EventSourceResponse(event_generator())
```

**Explanation**:
- **FastAPI**: Creates a web server to handle HTTP requests.
- **StaticFiles**: Serves frontend files from the `static` folder.
- **/scan Endpoint**: Receives form data via POST, constructs the `blc` command, and streams output.
- **Command Building**: Maps form inputs to `blc` options, handling multiple `--exclude` keywords by splitting comma-separated input.
- **Streaming**: Uses `asyncio.create_subprocess_exec` to run `blc`. Attempts to parse output as JSON (since `blc` can output JSON with `--verbose`) for structured data; falls back to raw text if parsing fails.
- **Error Handling**: Captures and streams stderr and exceptions as error events.

## Step 4: Frontend Implementation
The frontend will:
- Display a form with inputs for all `blc` options.
- Send form data to the backend via POST.
- Display streaming results in real-time using SSE.

### 4.1: HTML (`index.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Broken Link Checker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <div class="container mt-5">
        <h1>Broken Link Checker</h1>
        <form id="scan-form" class="mb-4">
            <div class="mb-3">
                <label for="url" class="form-label">URL to Scan</label>
                <input type="text" class="form-control" id="url" name="url" placeholder="https://example.com" required>
            </div>
            <div class="mb-3">
                <label for="exclude" class="form-label">Exclude Keywords (comma-separated)</label>
                <input type="text" class="form-control" id="exclude" name="exclude" placeholder="keyword1,keyword2">
            </div>
            <div class="mb-3">
                <label class="form-label">Filter Level</label>
                <select class="form-select" id="filter_level" name="filter_level">
                    <option value="0">0: Clickable links</option>
                    <option value="1" selected>1: Clickable + media, iframes, meta</option>
                    <option value="2">2: 1 + stylesheets, scripts, forms</option>
                    <option value="3">3: 2 + metadata</option>
                </select>
            </div>
            <div class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="exclude_external" name="exclude_external">
                    <label class="form-check-label" for="exclude_external">Exclude External Links</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="exclude_internal" name="exclude_internal">
                    <label class="form-check-label" for="exclude_internal">Exclude Internal Links</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="follow" name="follow">
                    <label class="form-check-label" for="follow">Follow Robot Exclusions</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="get" name="get">
                    <label class="form-check-label" for="get">Use GET Method</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="ordered" name="ordered">
                    <label class="form-check-label" for="ordered">Maintain Link Order</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="recursive" name="recursive">
                    <label class="form-check-label" for="recursive">Recursive Scan</label>
                </div>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="verbose" name="verbose">
                    <label class="form-check-label" for="verbose">Verbose Output</label>
                </div>
            </div>
            <div class="mb-3">
                <label for="requests" class="form-label">Concurrent Requests</label>
                <input type="number" class="form-control" id="requests" name="requests" value="10" min="1">
            </div>
            <div class="mb-3">
                <label for="host_requests" class="form-label">Host Concurrent Requests</label>
                <input type="number" class="form-control" id="host_requests" name="host_requests" value="5" min="1">
            </div>
            <div class="mb-3">
                <label for="user_agent" class="form-label">User Agent</label>
                <input type="text" class="form-control" id="user_agent" name="user_agent" value="Mozilla/5.0">
            </div>
            <button type="submit" class="btn btn-primary" id="start-btn">Start Scan</button>
            <button type="button" class="btn btn-danger" id="stop-btn" disabled>Stop Scan</button>
        </form>
        <div id="results" class="border p-3" style="max-height: 400px; overflow-y: auto;">
            <p>Results will appear here...</p>
        </div>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>
```

**Explanation**:
- Uses Bootstrap 5.3.0 via CDN for styling.
- Includes a form with inputs for all `blc` options:
  - Text input for URL (required) and `--exclude` (comma-separated keywords).
  - Dropdown for `--filter_level` (0–3).
  - Checkboxes for boolean options (`--exclude-external`, etc.).
  - Number inputs for `--requests` and `--host_requests` with defaults.
  - Text input for `--user_agent` with a default value.
- Provides "Start Scan" and "Stop Scan" buttons.
- Includes a `results` div with a fixed height and scrollable overflow.

### 4.2: CSS (`styles.css`)
```css
body {
    background-color: #f8f9fa;
}
#results {
    background-color: #fff;
    font-family: monospace;
    font-size: 14px;
}
.result-error {
    color: red;
}
.result-complete {
    color: green;
}
.result-broken {
    color: red;
    font-weight: bold;
}
.result-ok {
    color: green;
}
```

**Explanation**:
- Sets a light background for the body.
- Styles the results area with a monospace font for readability.
- Defines classes for errors (red), completion (green), broken links (red, bold), and valid links (green).

### 4.3: JavaScript (`script.js`)
```javascript
document.getElementById('scan-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const resultsDiv = document.getElementById('results');

    // Clear previous results
    resultsDiv.innerHTML = '<p>Scanning...</p>';
    startBtn.disabled = true;
    stopBtn.disabled = false;

    // Send form data to backend
    const response = await fetch('/scan', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        resultsDiv.innerHTML += '<p class="result-error">Failed to start scan.</p>';
        startBtn.disabled = false;
        stopBtn.disabled = true;
        return;
    }

    // Start SSE connection
    const source = new EventSource('/scan?' + new URLSearchParams(formData).toString());

    source.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const p = document.createElement('p');
        if (data.event === 'result') {
            try {
                const result = JSON.parse(data.data);
                // Handle structured JSON output
                p.textContent = `Link: ${result.url} - ${result.broken ? 'Broken' : 'OK'} (Status: ${result.status || 'N/A'}, Reason: ${result.reason || 'N/A'})`;
                p.classList.add(result.broken ? 'result-broken' : 'result-ok');
            } catch (e) {
                // Fallback for non-JSON output
                p.textContent = data.data;
            }
        } else if (data.event === 'error') {
            p.textContent = `Error: ${data.data}`;
            p.classList.add('result-error');
        } else if (data.event === 'complete') {
            p.textContent = data.data;
            p.classList.add('result-complete');
            source.close();
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
        resultsDiv.appendChild(p);
        resultsDiv.scrollTop = resultsDiv.scrollHeight;
    };

    source.onerror = () => {
        const p = document.createElement('p');
        p.textContent = 'Connection error. Please try again.';
        p.classList.add('result-error');
        resultsDiv.appendChild(p);
        source.close();
        startBtn.disabled = false;
        stopBtn.disabled = true;
    };

    // Stop button
    stopBtn.onclick = () => {
        source.close();
        const p = document.createElement('p');
        p.textContent = 'Scan stopped by user.';
        p.classList.add('result-error');
        resultsDiv.appendChild(p);
        startBtn.disabled = false;
        stopBtn.disabled = true;
    };
});
```

**Explanation**:
- Listens for form submission, prevents default behavior, and collects form data.
- Sends a POST request to `/scan` to initiate the scan.
- Establishes an SSE connection using `EventSource` with query parameters.
- Parses incoming messages:
  - For `result` events, attempts to parse JSON for structured output (e.g., link URL, broken status).
  - Falls back to raw text if JSON parsing fails.
  - Applies `result-broken` or `result-ok` classes based on link status.
- Handles errors and completion, closing the SSE connection when done.
- Implements the stop button to close the SSE connection and reset the UI.
- Scrolls the results div to show the latest output.

## Step 5: Run the Application
1. **Create the File Structure**:
   - Create the `static` folder and add `index.html`, `styles.css`, and `script.js`.
   - Create `app.py` in the project root.
2. **Start the Backend**:
   - In the terminal, navigate to `broken-link-checker-web`.
   - Run:
     ```
     uvicorn app:app --reload
     ```
     This starts the FastAPI server at `http://localhost:8000`.
3. **Test the App**:
   - Open a browser and go to `http://localhost:8000`.
   - Enter a URL (e.g., `https://example.com`).
   - Adjust options (e.g., check "Recursive Scan", set `--filter-level` to 2).
   - Click "Start Scan" and watch results stream into the results area.
   - Click "Stop Scan" to halt the process.
   - Example output:
     ```
     Link: https://example.com/page1 - Broken (Status: 404, Reason: HTTP_404)
     Link: https://example.com/page2 - OK (Status: 200, Reason: N/A)
     Scan completed
     ```

## Step 6: Debugging Tips
- **No Results**: Verify `broken-link-checker` is installed (`node_modules/broken-link-checker` exists).
- **Command Errors**: Check the terminal running `uvicorn` for `blc` error messages.
- **Streaming Issues**: Open browser developer tools (F12 > Console) to check for SSE errors.
- **Invalid URL**: Ensure the URL includes `http://` or `https://`.
- **JSON Parsing Errors**: If results look garbled, ensure `blc` output is being parsed correctly in `app.py`.

## Step 7: Enhancements (Optional)
- **Save Results**: Add a button to download results as a text file:
  ```javascript
  const saveBtn = document.createElement('button');
  saveBtn.textContent = 'Save Results';
  saveBtn.className = 'btn btn-secondary mt-3';
  saveBtn.onclick = () => {
      const text = resultsDiv.innerText;
      const blob = new Blob([text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'scan-results.txt';
      a.click();
      URL.revokeObjectURL(url);
  };
  resultsDiv.after(saveBtn);
  ```
- **Progress Bar**: Estimate progress for recursive scans by counting processed links.
- **Multiple URLs**: Modify the form to accept multiple URLs in a textarea and loop through them in the backend.
- **Enhanced Styling**: Add a loading spinner during scans using Bootstrap’s spinner component.

## Learning Outcomes
- **Python**: Built a web server with FastAPI, managed subprocesses, and streamed data with SSE.
- **HTML/JavaScript**: Created an interactive form, handled events, and updated the DOM dynamically.
- **Node.js Integration**: Interfaced Python with a Node.js module (`blc`).
- **Web Development**: Learned client-server communication, form handling, and real-time updates with SSE.
- **Debugging**: Gained experience troubleshooting server and client-side issues.

## Resources
- **FastAPI**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **SSE with FastAPI**: [sse-starlette.readthedocs.io](https://sse-starlette.readthedocs.io)
- **Broken Link Checker**: [npmjs.com/package/broken-link-checker](https://www.npmjs.com/package/broken-link-checker)
- **Bootstrap**: [getbootstrap.com](https://getbootstrap.com)
- **EventSource API**: [developer.mozilla.org/en-US/docs/Web/API/EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

This project is a fantastic way to combine Python, HTML, and JavaScript skills while building a practical tool. Have fun, and let me know if you need help debugging or adding features!