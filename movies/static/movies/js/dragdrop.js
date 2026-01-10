document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('film-list');
    if (!container) return;

    // Initialiser drag & drop
    Array.from(container.children).forEach(item => {
        item.setAttribute('draggable', true);

        item.addEventListener('dragstart', e => {
            e.dataTransfer.setData('text/plain', item.dataset.id);
        });

        item.addEventListener('dragover', e => {
            e.preventDefault();
        });

        item.addEventListener('drop', e => {
            e.preventDefault();
            const draggedId = e.dataTransfer.getData('text/plain');
            const draggedEl = container.querySelector(`[data-id='${draggedId}']`);
            container.insertBefore(draggedEl, item.nextSibling);
            saveOrder();
        });
    });

    function saveOrder() {
        const order = Array.from(container.children).map(c => c.dataset.id);
        fetch("/reorder/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ order: order })
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let c of cookies) {
                c = c.trim();
                if (c.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(c.slice(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
