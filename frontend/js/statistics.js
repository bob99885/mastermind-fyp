async function loadStatistics() {
    const container = document.getElementById("statistics");
    const analyticsContainer = document.getElementById("player-analytics");

    try {
        const response = await fetch("/statistics");
        const data = await response.json();
        renderPlayerAnalytics(data.player_analytics || {});

        const solverResults = data.solver_results || {};

        if (Object.keys(solverResults).length) {
            container.innerHTML = `
                <table>
                    <thead><tr><th>Solver</th><th>Average</th><th>Best</th><th>Worst Case</th><th>Runtime (s)</th></tr></thead>
                    <tbody>${Object.entries(solverResults).map(([solver, result]) => `
                        <tr><td>${solver}</td><td>${result.avg ?? "-"}</td><td>${result.best ?? "-"}</td><td>${result.worst ?? "-"}</td><td>${result.runtime ?? "-"}</td></tr>
                    `).join("")}</tbody>
                </table>
            `;
            return;
        }

        if (!data.results.length) {
            container.textContent = "No benchmark results are available yet.";
            return;
        }

        const headers = Object.keys(data.results[0]);
        container.innerHTML = `
            <table>
                <thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead>
                <tbody>${data.results.map((row) =>
                    `<tr>${headers.map((header) => `<td>${row[header]}</td>`).join("")}</tr>`
                ).join("")}</tbody>
            </table>
        `;
    } catch (error) {
        container.textContent = "Unable to load statistics.";
    }
}

function renderPlayerAnalytics(analytics) {
    const container = document.getElementById("player-analytics");
    const value = (item) => item ?? "-";
    container.innerHTML = `
        <div class="analytics-grid">
            <div class="analytics-stat"><strong>${value(analytics.games_played)}</strong><span>Games played</span></div>
            <div class="analytics-stat"><strong>${value(analytics.win_rate)}%</strong><span>Win rate</span></div>
            <div class="analytics-stat"><strong>${value(analytics.average_guesses)}</strong><span>Average guesses</span></div>
            <div class="analytics-stat"><strong>${value(analytics.fastest_win)}</strong><span>Fastest win</span></div>
            <div class="analytics-stat"><strong>${value(analytics.most_common_opening)}</strong><span>Common opening</span></div>
            <div class="analytics-stat"><strong>${value(analytics.most_used_colour)}</strong><span>Most used colour</span></div>
        </div>
        <p class="analytics-note">Human results are recorded after each completed guess sequence and can be compared with the benchmark solvers below.</p>
    `;
}

loadStatistics();