document.getElementById("scan-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;

    // Build JSON payload
    const payload = {
        url: form.url.value,
        exclude: form.exclude.value,
        filter_level: parseInt(form.filter_level.value),
        exclude_external: form.exclude_external.checked,
        exclude_internal: form.exclude_internal.checked,
        follow: form.follow.checked,
        get: form.get.checked,
        ordered: form.ordered.checked,
        recursive: form.recursive.checked,
        verbose: form.verbose.checked,
        requests: parseInt(form.requests.value),
        host_requests: parseInt(form.host_requests.value),
        user_agent: form.user_agent.value
    };

    // Prepare EventSource to stream output
    const resultsBox = document.getElementById("results");
    resultsBox.innerHTML = "<p>Scanning...</p>";

    const stopBtn = document.getElementById("stop-btn");
    stopBtn.disabled = false;

    const controller = new AbortController();

    stopBtn.onclick = () => {
        controller.abort();
        stopBtn.disabled = true;
        resultsBox.innerHTML += "<p><em>Scan stopped by user.</em></p>";
    };

    fetch("/scan", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload),
        signal: controller.signal
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        resultsBox.innerHTML = "";

        const readChunk = () => {
            reader.read().then(({ done, value }) => {
                if (done) return;
                const text = decoder.decode(value);
                const lines = text.trim().split("\n\n");

                lines.forEach(chunk => {
                    if (chunk.startsWith("data:")) {
                        const content = chunk.replace("data: ", "").trim();
                        resultsBox.innerHTML += `<p>${content}</p>`;
                    }
                });

                readChunk();
            });
        };

        readChunk();
    }).catch(err => {
        if (err.name !== "AbortError") {
            resultsBox.innerHTML += `<p class="text-danger">Error: ${err.message}</p>`;
        }
    });
});
