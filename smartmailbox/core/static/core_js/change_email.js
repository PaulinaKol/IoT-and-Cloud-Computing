document.addEventListener('DOMContentLoaded', function () {
    function showModal(title, message, onOk) {
        const modal = document.getElementById('modal');
        const okBtn = document.getElementById('modal-ok-btn');
        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-message').innerHTML = message;
        modal.style.display = 'block';

        function closeModal() {
            modal.style.display = 'none';
            if (onOk) onOk();
            window.onclick = null;
        }

        okBtn.onclick = closeModal;
        window.onclick = function(event) {
            if (event.target == modal) {
                closeModal();
            }
        };
    }

    if (window.emailChangeStatus === "success") {
        showModal("Sukces!", "Adres email został zmieniony.", function () {
            window.location.href = "/user_settings/";
        });
    } else if (window.emailChangeStatus === "error" && Object.keys(window.emailChangeErrors).length > 0) {
        let msg = "<ul>";
        for (let field in window.emailChangeErrors) {
            for (let err of window.emailChangeErrors[field]) {
                msg += "<li>" + err.message + "</li>";
            }
        }
        msg += "</ul>";
        showModal("Błąd!", msg);
    }
});
