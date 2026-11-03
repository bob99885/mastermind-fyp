async function runSolver() {
    const solver = document.getElementById("solver").value;
    const output = document.getElementById("output");
    const isLocalFrontend = ["localhost", "127.0.0.1"].includes(window.location.hostname) && window.location.port !== "5001";
    const apiBaseUrl = window.location.protocol === "file:" || isLocalFrontend
        ? "http://127.0.0.1:5001"
        : window.location.origin;

    try {
        const response = await fetch(`${apiBaseUrl}/solver/run`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ solver })
        });
        const responseText = await response.text();
        let data;
        try {
            data = responseText ? JSON.parse(responseText) : { error: `Server returned an empty response (${response.status}).` };
        } catch {
            data = { error: `Server returned an invalid response (${response.status}).` };
        }

        if (!response.ok) {
            throw new Error(data.error || "Unable to run solver.");
        }

        output.innerHTML = `
            <h3>${data.solver} solver</h3>
            <div class="solver-history">
                ${data.history.map((entry, index) => `
                    <div class="solver-row">
                        <span class="solver-step">Guess #${index + 1}</span>
                        ${renderColourPegs(entry.guess)}
                        ${renderFeedbackPegs(entry.black, entry.white)}
                        ${entry.strategy ? `<span class="solver-details"><strong>${entry.strategy}</strong>: ${entry.reason}<br>Candidate space: ${entry.candidates_before}</span>` : ""}
                    </div>
                `).join("")}
            </div>
            <h3 class="solver-result">${data.solved ? `Solved in ${data.guesses} guesses` : "Did not solve the game"}</h3>
        `;
    } catch (error) {
        output.textContent = error.message === "Failed to fetch"
            ? "Cannot connect to the Flask server. Start it with: python3 app.py"
            : error.message;
    }
}

function renderColourPegs(guess) {
    const colourNames = ["", "Red", "Blue", "Green", "Yellow", "Purple", "Black"];
    const accessibleNames = guess.map((colour) => colourNames[colour]);
    return `
        <div class="solver-guess-display">
            <span class="solver-code">${guess.join("")}</span>
            <div class="solver-colours" role="img" aria-label="${accessibleNames.join(", ")}">
                ${guess.map((colour) => `
                    <span class="peg colour-${colourNames[colour].toLowerCase()}" aria-hidden="true" title="${colourNames[colour]}"></span>
                `).join("")}
            </div>
        </div>
    `;
}

function renderFeedbackPegs(black, white) {
    return `
        <div class="solver-feedback">
            <div class="solver-feedback-pegs" aria-hidden="true">
                ${'<span class="peg peg-black"></span>'.repeat(black)}
                ${'<span class="peg peg-white"></span>'.repeat(white)}
            </div>
            <span class="solver-feedback-counts">Black: ${black} | White: ${white}</span>
        </div>
    `;
}