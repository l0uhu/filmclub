document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("film-list");
    if (!container) return;

    const reorderUrl = container.dataset.reorderUrl;
    const csrfToken = container.dataset.csrfToken;

    let draggedEl = null;

    Array.from(container.children).forEach(item => {
        item.setAttribute("draggable", true);

        item.addEventListener("dragstart", e => {
            draggedEl = item;
            e.dataTransfer.effectAllowed = "move";
        });

        item.addEventListener("dragover", e => e.preventDefault());

        item.addEventListener("drop", e => {
            e.preventDefault();
            if (!draggedEl || draggedEl === item) return;

            const children = Array.from(container.children);
            const draggedIndex = children.indexOf(draggedEl);
            const targetIndex = children.indexOf(item);

            if (draggedIndex < targetIndex) {
                container.insertBefore(draggedEl, item.nextSibling);
            } else {
                container.insertBefore(draggedEl, item);
            }

            // sauvegarde
            saveOrder();
        });
    });

    function saveOrder() {
        const order = Array.from(container.children).map(c => c.dataset.id);

        fetch(reorderUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ order })
        });
    }
});
