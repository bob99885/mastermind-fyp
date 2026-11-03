document.addEventListener("DOMContentLoaded", () => {
    const dialog = document.getElementById("rules-dialog");

    document.getElementById("rules-button").addEventListener("click", () => dialog.showModal());
    document.getElementById("close-rules").addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) dialog.close();
    });
});
