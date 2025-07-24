import subprocess
from flask import Flask, request, Response, send_from_directory, stream_with_context

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()

    url = data.get("url", "")
    exclude_external = data.get("exclude_external", False)
    exclude_internal = data.get("exclude_internal", False)
    recursive = data.get("recursive", False)
    ordered = data.get("ordered", False)
    verbose = data.get("verbose", False)
    follow = data.get("follow", False)
    get = data.get("get", False)
    filter_level = data.get("filter_level", -1)
    requests = data.get("requests", 0)
    host_requests = data.get("host_requests", 0)
    user_agent = data.get("user_agent", "Mozilla/5.0")
    exclude_keywords = data.get("exclude", "").split(",")

    def generate():
        for line in call_blc(url, exclude_external, exclude_internal, recursive, ordered,
        verbose, follow, get, filter_level, requests,
        host_requests, user_agent, exclude_keywords):
            yield f"data: {line.strip()}\n\n"
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

def call_blc(
    url, exclude_external, exclude_internal, recursive, ordered,
    verbose, follow, get, filter_level, requests,
    host_requests, user_agent, keywords
):
    command = ["blc", url]

    if exclude_external:
        command.append("--exclude-external")
    if exclude_internal:
        command.append("--exclude-internal")
    if recursive:
        command.append("--recursive")
    if ordered:
        command.append("--ordered")
    if verbose:
        command.append("--verbose")
    if follow:
        command.append("--follow")
    if get:
        command.append("--get")
    if filter_level != -1:
        command.extend(["--filter-level", str(filter_level)])
    if requests > 0:
        command.extend(["--requests", str(requests)])
    if host_requests > 0:
        command.extend(["--host-requests", str(host_requests)])
    if user_agent:
        command.extend(["--user-agent", user_agent])
    for item in keywords:
        if item.strip():
            command.extend(["--exclude", item.strip()])

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=False
    )

    for line in process.stdout:
        if "getaddrinfo ENOTFOUND" in line:
            yield "This Url cannot be reached. if this is your input URL, please check for errors."
        else:
            yield line
    process.wait()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)