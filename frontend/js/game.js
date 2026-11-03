const isLocalFrontend = ["localhost", "127.0.0.1"].includes(window.location.hostname) && window.location.port !== "5001";
const API_BASE_URL = window.location.protocol === "file:" || isLocalFrontend
    ? "http://127.0.0.1:5001"
    : window.location.origin;
const COLOUR_NAMES = ["", "Red", "Blue", "Green", "Yellow", "Purple", "Black"];
const INITIAL_COLOUR_STOCK = 10;
let currentGuess = [];
let secretGuess = [];
let selectedMode = "computer";
let gameFinished = false;
let guessHistory = [];
let committedColourInventory = Object.fromEntries(
    COLOUR_NAMES.slice(1).map((_, index) => [index + 1, INITIAL_COLOUR_STOCK])
);

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("#secret-palette .colour-swatch").forEach((swatch) => {
        swatch.addEventListener("click", () => selectSecretColour(Number(swatch.dataset.colour)));
    });
    document.getElementById("history").addEventListener("click", (event) => {
        const slot = event.target.closest("[data-guess-slot]");
        if (slot) cycleBoardSlot(Number(slot.dataset.guessSlot));
    });
    document.getElementById("submit-button").addEventListener("click", submitGuess);
    document.getElementById("new-game-button").addEventListener("click", newGame);
    document.getElementById("new-game-top-button").addEventListener("click", startNewGame);
    document.getElementById("computer-mode-button").addEventListener("click", () => startComputerGame());
    document.getElementById("player-mode-button").addEventListener("click", showPlayerSetup);
    document.getElementById("start-player-game-button").addEventListener("click", startPlayerGame);
    document.getElementById("advisor-recommendations").addEventListener("click", (event) => {
        const button = event.target.closest("[data-advisor-guess]");
        if (!button) return;
        currentGuess = button.dataset.advisorGuess.split(",").map(Number);
        renderGuess();
        document.getElementById("feedback").textContent = "Suggested guess loaded. Submit it or adjust the colours.";
    });
    document.querySelectorAll("#secret-slots .guess-slot").forEach((slot, index) => {
        slot.addEventListener("click", () => removeSecretColour(index));
    });
    renderGuess();
    renderSecretGuess();

    const requestedMode = new URLSearchParams(window.location.search).get("mode");
    if (requestedMode === "computer") startComputerGame();
    if (requestedMode === "player") showPlayerSetup();
});

function showGame() {
    document.getElementById("mode-panel").hidden = true;
    document.getElementById("game-workspace").hidden = false;
    document.getElementById("game-panel").hidden = false;
}

async function startComputerGame() {
    selectedMode = "computer";
    await createGame();
}

function showPlayerSetup() {
    document.getElementById("mode-choice").hidden = true;
    document.getElementById("secret-setup").hidden = false;
    document.getElementById("computer-mode-button").disabled = true;
    document.getElementById("player-mode-button").disabled = true;
    document.getElementById("mode-feedback").textContent = "";
    document.getElementById("setup-feedback").textContent = "";
}

async function startPlayerGame() {
    if (secretGuess.length !== 4) {
        document.getElementById("setup-feedback").textContent = "Choose four colours before starting the game.";
        return;
    }
    selectedMode = "player";
    const started = await createGame(secretGuess);
    if (!started) return;
    secretGuess = [];
    renderSecretGuess();
    currentGuess = [];
    renderGuess();
}

async function createGame(secret = null) {
    try {
        const response = await fetch(`${API_BASE_URL}/new-game`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(secret ? { mode: selectedMode, secret } : { mode: selectedMode })
        });
        const data = await readJson(response);
        if (!response.ok) throw new Error(data.error || "Unable to start the game.");
        setColourInventory(data.colour_inventory);
        gameFinished = false;
        document.getElementById("new-game-top-button").hidden = true;
        document.getElementById("submit-button").disabled = false;
        document.getElementById("mode-feedback").textContent = "";
        showGame();
        currentGuess = [];
        guessHistory = [];
        renderGuess();
        document.getElementById("attempt-count").textContent = "Attempt 1";
        document.getElementById("feedback").textContent = selectedMode === "player" ? "Player 2, crack the code." : "Computer has chosen a secret code.";
        renderHistory(data.history || []);
        await updateAdvisor();
        await updateAlgorithmAnalysis();
        return true;
    } catch (error) {
        const message = error.message === "Failed to fetch"
            ? "Cannot connect to the Flask server. Start it with: python3 app.py"
            : error.message;
        const feedback = document.getElementById("game-workspace").hidden
            ? (document.getElementById("secret-setup").hidden
                ? document.getElementById("mode-feedback")
                : document.getElementById("setup-feedback"))
            : document.getElementById("feedback");
        feedback.textContent = message;
        return false;
    }
}

function selectSecretColour(colour) {
    if (secretGuess.length >= 4) return;
    secretGuess.push(colour);
    renderSecretGuess();
}

function renderGuess() {
    renderHistory(guessHistory);
    renderColourDistribution();
}

function cycleBoardSlot(index) {
    if (gameFinished || index < 0 || index >= 4 || index > currentGuess.length) return;
    const currentColour = currentGuess[index] || 0;
    currentGuess.splice(index, 1);
    const availableInventory = getAvailableColourInventory();
    let nextColour = 0;
    for (let offset = 1; offset <= COLOUR_NAMES.length; offset += 1) {
        const candidate = (currentColour + offset) % COLOUR_NAMES.length;
        if (candidate === 0 || availableInventory[candidate] > 0) {
            nextColour = candidate;
            break;
        }
    }
    if (nextColour) currentGuess[index] = nextColour;
    renderGuess();
}

function setColourInventory(inventory) {
    if (!inventory) return;
    committedColourInventory = Object.fromEntries(
        COLOUR_NAMES.slice(1).map((_, index) => {
            const colour = index + 1;
            return [colour, Number(inventory[colour] ?? INITIAL_COLOUR_STOCK)];
        })
    );
    renderColourDistribution();
}

function getAvailableColourInventory() {
    const inventory = { ...committedColourInventory };
    currentGuess.forEach((colour) => {
        inventory[colour] -= 1;
    });
    return inventory;
}

function renderColourDistribution() {
    const distribution = document.getElementById("colour-distribution");
    if (!distribution) return;

    const inventory = getAvailableColourInventory();
    const total = Object.values(inventory).reduce((sum, count) => sum + count, 0);
    distribution.innerHTML = COLOUR_NAMES.slice(1).map((name, index) => {
        const colour = index + 1;
        const count = Math.max(0, inventory[colour]);
        const probability = total ? count / total * 100 : 0;
        return `
            <div class="distribution-row" aria-label="${name}: ${count} of ${total} pegs, ${probability.toFixed(1)} percent">
                <span class="peg colour-${name.toLowerCase()}" aria-hidden="true"></span>
                <span>${name}</span>
                <span class="distribution-count">${count}/${total}</span>
                <strong class="distribution-probability">${probability.toFixed(1)}%</strong>
                <span class="distribution-track" aria-hidden="true"><span class="distribution-fill colour-${name.toLowerCase()}" style="width: ${count / INITIAL_COLOUR_STOCK * 100}%"></span></span>
            </div>
        `;
    }).join("");

    const held = currentGuess.length;
    document.getElementById("pool-total").textContent = `Available: ${total} / 60 pegs${held ? ` · ${held} held in this guess` : ""}`;
}

function renderSecretGuess() {
    document.querySelectorAll("#secret-slots .guess-slot").forEach((slot, index) => {
        const colour = secretGuess[index];
        slot.className = `guess-slot${colour ? ` colour-${COLOUR_NAMES[colour].toLowerCase()}` : " empty"}`;
        slot.setAttribute("aria-label", colour ? `${COLOUR_NAMES[colour]}, remove` : `Secret slot ${index + 1}`);
    });
    const remaining = 4 - secretGuess.length;
    const status = document.getElementById("secret-selection-status");
    if (status) status.textContent = remaining ? `${remaining} slot${remaining === 1 ? "" : "s"} left` : "Secret ready";
}

async function submitGuess() {

    const guess = [...currentGuess];

    if (guess.length !== 4) {
        document.getElementById("feedback").textContent =
            "Choose four colours before submitting.";
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/guess`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ guess })
        });

        const data = await readJson(response);

        if (!response.ok) {
            throw new Error(data.error || "Unable to submit guess.");
        }

        document.getElementById("feedback").innerHTML = `
            <strong>${data.won ? "Code cracked" : "Feedback"}</strong>
            <div class="feedback-pegs" aria-label="${data.black} exact and ${data.white} colour-only matches">
                ${renderPegs(data.black, data.white)}
            </div>
            <span>${data.black} exact, ${data.white} colour-only</span>
        `;

        if (data.won) {
            document.getElementById("feedback").innerHTML += `<p class="success-message">You solved the code in ${data.attempts} attempts.</p>`;
        }

        gameFinished = data.game_over;
        document.getElementById("new-game-top-button").hidden = !data.won;
        document.getElementById("submit-button").disabled = gameFinished;
        currentGuess = [];
        setColourInventory(data.colour_inventory);
        renderGuess();
        document.getElementById("attempt-count").textContent = `Attempt ${data.attempts + 1}`;
        renderHistory(data.history);
        await updateAdvisor();
        await updateAlgorithmAnalysis();
    } catch (error) {
        document.getElementById("feedback").textContent = error.message === "Failed to fetch"
            ? "Cannot connect to the Flask server. Start it with: python3 app.py"
            : error.message;
    }
}

async function newGame() {
    document.getElementById("game-workspace").hidden = true;
    document.getElementById("game-panel").hidden = true;
    document.getElementById("mode-panel").hidden = false;
    document.getElementById("secret-setup").hidden = true;
    document.getElementById("mode-choice").hidden = false;
    document.getElementById("computer-mode-button").disabled = false;
    document.getElementById("player-mode-button").disabled = false;
    gameFinished = false;
    document.getElementById("new-game-top-button").hidden = true;
    document.getElementById("submit-button").disabled = false;
    currentGuess = [];
    secretGuess = [];
    renderGuess();
    renderSecretGuess();
    document.getElementById("mode-feedback").textContent = "";
    document.getElementById("setup-feedback").textContent = "";
    document.getElementById("advisor-status").textContent = "Waiting for a game.";
    document.getElementById("advisor-recommendations").innerHTML = "";
}

async function startNewGame() {
    if (selectedMode === "computer") {
        await startComputerGame();
        return;
    }

    await newGame();
    showPlayerSetup();
    document.getElementById("setup-feedback").textContent = "Choose a new secret code to start another game.";
}

async function updateAdvisor() {
    const status = document.getElementById("advisor-status");
    const recommendations = document.getElementById("advisor-recommendations");
    const criteriaLeaders = document.getElementById("criteria-leaders");
    status.textContent = "Calculating suggestions...";
    recommendations.innerHTML = "";
    criteriaLeaders.innerHTML = "";

    try {
        const response = await fetch(`${API_BASE_URL}/game/advice`);
        const data = await readJson(response);
        if (!response.ok) throw new Error(data.error || "Unable to calculate suggestions.");
        setColourInventory(data.colour_inventory);
        const criteriaNames = {
            hybrid: "HERF hybrid",
            entropy: "Entropy",
            expected_remaining: "Expected candidates",
            minimax: "Minimax"
        };
        criteriaLeaders.innerHTML = Object.entries(data.criteria || {}).map(
            ([criterion, guess]) => `
                <div class="criteria-row">
                    <span>${criteriaNames[criterion] || criterion}</span>
                    <strong>${guess.join("")}</strong>
                </div>
            `
        ).join("");

        if (data.game_over) {
            status.textContent = data.solved
                ? "Code solved. Start a new game to play again."
                : "Fewer than four pegs remain. Start a new game to continue.";
            return;
        }

        status.textContent = `Based on ${data.candidate_count.toLocaleString()} possible codes.`;
        recommendations.innerHTML = data.recommendations.map((option, index) => `
            <article class="advice-choice">
                <div class="advice-choice-heading">
                    <span>Option ${index + 1}</span>
                    <strong>${option.expected_reduction}%</strong>
                </div>
                <span class="advice-metric-label">expected options ruled out</span>
                <div class="advice-code-row">
                    <span class="advice-code">${option.guess.join("")}</span>
                    <div class="mini-guess" role="img" aria-label="${option.guess.map((colour) => COLOUR_NAMES[colour]).join(", ")}">
                        ${option.guess.map((colour) => `<span class="peg colour-${COLOUR_NAMES[colour].toLowerCase()}" aria-hidden="true"></span>`).join("")}
                    </div>
                </div>
                <p class="advice-reason">${option.reason}</p>
                <div class="advice-metrics">
                    <span>${option.entropy} bits entropy</span>
                    <span>${option.expected_reduction}% ruled out</span>
                    <span>${option.expected_remaining} expected left</span>
                    <span>${option.worst_case_remaining} worst case</span>
                </div>
                <div class="advice-metrics">
                    <span>Entropy contribution: ${(option.criterion_scores.hybrid_contributions.entropy * 100).toFixed(1)}%</span>
                    <span>Elimination contribution: ${(option.criterion_scores.hybrid_contributions.expected_elimination * 100).toFixed(1)}%</span>
                    <span>Minimax contribution: ${(option.criterion_scores.hybrid_contributions.minimax_reduction * 100).toFixed(1)}%</span>
                </div>
                <details class="outcome-details">
                    <summary>Possible outcome distribution</summary>
                    <div class="outcome-distribution">
                        ${option.distribution.map((outcome) => `
                            <div class="outcome-row">
                                <span>${outcome.black}B ${outcome.white}W</span>
                                <span class="outcome-bar"><i style="width: ${outcome.probability}%"></i></span>
                                <strong>${outcome.probability}%</strong>
                            </div>
                        `).join("")}
                    </div>
                </details>
                ${option.solve_chance ? `<p class="advice-solve-chance">Immediate solve chance: ${option.solve_chance}%</p>` : ""}
                <button class="suggestion-action" type="button" data-advisor-guess="${option.guess.join(",")}">Use this guess</button>
            </article>
        `).join("");
    } catch (error) {
        status.textContent = error.message === "Failed to fetch"
            ? "Advisor unavailable. Check that the Flask server is running."
            : error.message;
    }
}

async function updateAlgorithmAnalysis() {
    const summary = document.getElementById("analyst-summary");
    const container = document.getElementById("algorithm-analysis");
    try {
        const response = await fetch(`${API_BASE_URL}/game/algorithm-analysis`);
        const data = await readJson(response);
        if (!response.ok) throw new Error(data.error || "Unable to compare algorithms.");
        document.getElementById("analyst-state").textContent =
            `n = ${data.n} · ${data.candidate_count} candidates`;
        summary.textContent = "Both algorithms are checked against entropy, expected elimination, expected remaining candidates, and minimax worst-case size.";
        container.innerHTML = Object.values(data.algorithms).map((algorithm) => `
            <article class="algorithm-card">
                <div class="algorithm-card-heading">
                    <div>
                        <p class="eyebrow">${algorithm.name}</p>
                        <strong class="algorithm-guess">${algorithm.recommended_guess.join("")}</strong>
                    </div>
                    <span class="algorithm-label">Recommended move</span>
                </div>
                <p class="algorithm-explanation">${algorithm.explanation}</p>
                <div class="algorithm-metrics">
                    <span>Entropy: ${algorithm.metrics.entropy_bits} bits</span>
                    <span>Ruled out: ${algorithm.metrics.expected_elimination_percent}%</span>
                    <span>Expected left: ${algorithm.metrics.expected_remaining}</span>
                    <span>Worst case: ${algorithm.metrics.worst_case_remaining}</span>
                </div>
                <h3>All possible feedback distributions</h3>
                <div class="full-distribution">
                    ${algorithm.distribution.map((outcome) => `
                        <div class="full-distribution-row">
                            <span>${outcome.black}B ${outcome.white}W</span>
                            <span class="outcome-bar"><i style="width: ${outcome.probability}%"></i></span>
                            <strong>${outcome.count} (${outcome.probability}%)</strong>
                        </div>
                    `).join("")}
                </div>
            </article>
        `).join("");
    } catch (error) {
        summary.textContent = error.message === "Failed to fetch"
            ? "Analyst unavailable. Check that the Flask server is running."
            : error.message;
        container.innerHTML = "";
    }
}

async function readJson(response) {
    const text = await response.text();
    try {
        return text ? JSON.parse(text) : { error: `Server returned an empty response (${response.status}).` };
    } catch {
        return { error: `Server returned an invalid response (${response.status}).` };
    }
}

function renderHistory(history) {
    guessHistory = history;
    const boardRows = Array.from({ length: 10 }, (_, index) => {
        const entry = history[index];
        const active = !gameFinished && index === history.length;
        const guess = entry
            ? entry.guess.map((colour) =>
                `<button class="board-hole filled colour-${COLOUR_NAMES[colour].toLowerCase()}" type="button" title="${COLOUR_NAMES[colour]}" aria-label="${COLOUR_NAMES[colour]}"></button>`
            ).join("")
            : active
                ? Array.from({ length: 4 }, (_, slot) => {
                    const colour = currentGuess[slot];
                    return `<button class="board-hole${colour ? ` filled colour-${COLOUR_NAMES[colour].toLowerCase()}` : ""}" type="button" data-guess-slot="${slot}" aria-label="${colour ? COLOUR_NAMES[colour] : `Empty guess slot ${slot + 1}`}"></button>`;
                }).join("")
                : '<span class="board-hole"></span>'.repeat(4);
        const feedback = entry
            ? renderPegs(entry.black, entry.white, "board-feedback-peg")
            : '<span class="board-feedback-peg"></span>'.repeat(4);
        return `
            <div class="board-row${entry ? " played" : ""}${active ? " active" : ""}" aria-label="Attempt ${index + 1}${entry ? `, ${entry.black} exact and ${entry.white} colour only` : active ? ", current guess" : ", empty"}">
                <span class="board-number">${index + 1}</span>
                <div class="board-guess">${guess}</div>
                <div class="board-feedback">${feedback}</div>
            </div>
        `;
    }).join("");
    document.getElementById("history").innerHTML = boardRows;
}

function renderPegs(black, white, className = "peg") {
    return `${`<span class="${className} peg-black"></span>`.repeat(black)}${`<span class="${className} peg-white"></span>`.repeat(white)}`;
}

function removeSecretColour(index) {
    if (index < secretGuess.length) {
        secretGuess.splice(index, 1);
        renderSecretGuess();
    }
}