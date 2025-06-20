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

    if (window.passwordChangeStatus === "success") {
        showModal("Sukces!", "Hasło zostało zmienione.", function () {
            window.location.href = "/user_settings/";
        });
    } else if (window.passwordChangeStatus === "error" && Object.keys(window.passwordChangeErrors).length > 0) {
        let msg = "<ul>";
        for (let field in window.passwordChangeErrors) {
            for (let err of window.passwordChangeErrors[field]) {
                msg += "<li>" + err.message + "</li>";
            }
        }
        msg += "</ul>";
        showModal("Błąd!", msg);
    }
});
