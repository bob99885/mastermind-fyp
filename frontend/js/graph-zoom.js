document.addEventListener("DOMContentLoaded", () => {
    const dialog = document.createElement("dialog");
    dialog.className = "graph-dialog";
    dialog.innerHTML = `
        <div class="graph-dialog-header">
            <span id="graph-dialog-title">Chart</span>
            <div class="graph-dialog-actions">
                <button id="graph-zoom-out" type="button" aria-label="Zoom out">−</button>
                <button id="graph-zoom-reset" type="button" aria-label="Reset zoom">100%</button>
                <button id="graph-zoom-in" type="button" aria-label="Zoom in">+</button>
                <button id="graph-dialog-close" class="graph-dialog-close" type="button" aria-label="Close chart">×</button>
            </div>
        </div>
        <div class="graph-viewport"><img class="graph-dialog-image" alt=""></div>
    `;
    document.body.appendChild(dialog);

    const image = dialog.querySelector(".graph-dialog-image");
    const viewport = dialog.querySelector(".graph-viewport");
    let zoom = 1;

    function updateZoom() {
        const baseWidth = Math.max(viewport.clientWidth, 1);
        image.style.setProperty("width", `${Math.round(baseWidth * zoom)}px`, "important");
        dialog.querySelector("#graph-zoom-reset").textContent = `${Math.round(zoom * 100)}%`;
    }

    function openChart(chart) {
        image.src = chart.src;
        image.alt = chart.alt;
        dialog.querySelector("#graph-dialog-title").textContent = chart.alt || "Chart";
        zoom = 1;
        dialog.showModal();
        updateZoom();
        image.addEventListener("load", updateZoom, { once: true });
    }

    document.querySelectorAll(".graph-zoomable").forEach((chart) => {
        chart.addEventListener("click", () => openChart(chart));
        chart.title = "Click to enlarge chart";
    });

    dialog.querySelector("#graph-zoom-in").addEventListener("click", () => {
        zoom = Math.min(3, zoom + .25);
        updateZoom();
    });
    dialog.querySelector("#graph-zoom-out").addEventListener("click", () => {
        zoom = Math.max(1, zoom - .25);
        updateZoom();
    });
    dialog.querySelector("#graph-zoom-reset").addEventListener("click", () => {
        zoom = 1;
        updateZoom();
        viewport.scrollTo({ top: 0, left: 0, behavior: "smooth" });
    });
    dialog.querySelector("#graph-dialog-close").addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) dialog.close();
    });
    dialog.addEventListener("wheel", (event) => {
        if (!event.ctrlKey) return;
        event.preventDefault();
        zoom = Math.max(1, Math.min(3, zoom + (event.deltaY < 0 ? .1 : -.1)));
        updateZoom();
    }, { passive: false });
});