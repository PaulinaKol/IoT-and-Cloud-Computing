document.addEventListener('DOMContentLoaded', function () {
    function showModal(title, message, onOk) {
        const modal = document.getElementById('modal');
        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-message').innerHTML = message;
        modal.style.display = 'block';

        document.getElementById('modal-ok-btn').onclick = () => {
            modal.style.display = 'none';
            if (onOk) onOk();
        };

        window.onclick = function (e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        };
    }

    const translations = {
        "The two password fields didn’t match.": "Hasła nie są identyczne.",
        "This password is too short. It must contain at least 8 characters.": "Hasło musi mieć co najmniej 8 znaków.",
        "This password is too common.": "Hasło jest zbyt popularne.",
        "This password is entirely numeric.": "Hasło nie może składać się wyłącznie z cyfr.",
        "This password is too similar to your other personal information.": "Hasło jest zbyt podobne do danych osobowych.",
        "Your old password was entered incorrectly. Please enter it again.": "Stare hasło zostało podane niepoprawnie. Spróbuj ponownie."
    };

    const translate = (msg) => translations[msg.trim()] || msg;

    if (window.passwordChangeStatus === "success") {
        showModal("Sukces!", "Hasło zostało zmienione.", () => {
            window.location.href = "/user_settings/";
        });
    } else if (window.passwordChangeStatus === "error") {
        let msg = "<ul>";
        for (let field in window.passwordChangeErrors) {
            for (let err of window.passwordChangeErrors[field]) {
                msg += "<li>" + translate(err.message) + "</li>";
            }
        }
        msg += "</ul>";
        showModal("Błąd!", msg);
    }
});
