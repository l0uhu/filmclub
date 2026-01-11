document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("film-list");
    if (!container) return;

    const reorderUrl = container.dataset.reorderUrl;
    const csrfToken = container.dataset.csrfToken;

    // Init SortableJS
    new Sortable(container, {
        animation: 150,
        ghostClass: 'sortable-ghost',
        onEnd: function(evt) {
            // Sauvegarder l'ordre après drag
            const order = Array.from(container.children).map(c => c.dataset.id);

            fetch(reorderUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ order })
            }).then(resp => {
                if (!resp.ok) console.error("Erreur lors de la sauvegarde de l'ordre");
            });
        }
    });
});
