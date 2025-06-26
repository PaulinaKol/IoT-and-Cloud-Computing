document.addEventListener('DOMContentLoaded', function () {
    function showModal(title, message) {
        const modal = document.getElementById('modal');
        const okBtn = document.getElementById('modal-ok-btn');
        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-message').innerHTML = message;
        modal.style.display = 'block';

        function closeModal() {
            modal.style.display = 'none';
            window.onclick = null;
        }

        okBtn.onclick = closeModal;

        window.onclick = function(event) {
            if (event.target == modal) {
                closeModal();
            }
        };
    }

    if (window.deleteStatus === "error" && Object.keys(window.deleteErrors).length > 0) {
        let msg = "<ul>";
        for (let field in window.deleteErrors) {
            for (let err of window.deleteErrors[field]) {
                msg += "<li>" + err.message + "</li>";
            }
        }
        msg += "</ul>";
        showModal("Błąd!", msg);
    }
});
