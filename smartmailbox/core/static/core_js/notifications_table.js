document.addEventListener('DOMContentLoaded', function () {
function reloadNotificationsTable() {
    fetch('/notifications_table/')
      .then(resp => resp.json())
      .then(data => {
          document.getElementById('notifications-table-container').innerHTML = data.html;
          addDeleteSelectedHandler();
      });
}

function addDeleteSelectedHandler() {
    console.log("Podpinam handler do przycisku Usuń zaznaczone...");
    const deleteBtn = document.getElementById('delete-selected');
    if (deleteBtn) {
        deleteBtn.onclick = function () {
            // Zbierz zaznaczone checkboxy
            const checked = document.querySelectorAll('input[name="notification_ids"]:checked');
            const ids = Array.from(checked).map(cb => cb.value);
            if (ids.length === 0) {
                alert('Zaznacz powiadomienia do usunięcia.');
                return;
            }
            // Przygotuj dane do POST
            const formData = new FormData();
            ids.forEach(id => formData.append('notification_ids', id));

            fetch('/delete_notifications/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: formData
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.success) {
                    reloadNotificationsTable();
                } else {
                    alert(data.error || 'Błąd przy usuwaniu powiadomień.');
                }
            });
        };
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
addDeleteSelectedHandler();
});
