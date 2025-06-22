// Modal do usuwania urządzenia:
let currentDeviceId = null;
let currentDeviceName = null;
let selectedNotificationIds = new Set();

function showModal(deviceId, deviceName) {
    currentDeviceId = deviceId;
    currentDeviceName = deviceName;
    document.getElementById('modalMessage').innerText =
        `Czy napewno chcesz wyrejestrować urządzenie "${deviceName}" (ID: ${deviceId})?`;
    document.getElementById('myModal').style.display = "block";
}

function hideModal() {
    document.getElementById('myModal').style.display = "none";
    currentDeviceId = null;
    currentDeviceName = null;
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

document.getElementById('confirmBtn').onclick = function() {
    if (currentDeviceId) {
        const form = document.getElementById(`delete-form-${currentDeviceId}`);
        if (!form.querySelector('input[name="csrfmiddlewaretoken"]')) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrfmiddlewaretoken';
            input.value = getCookie('csrftoken');
            form.appendChild(input);
        } else {
            form.querySelector('input[name="csrfmiddlewaretoken"]').value = getCookie('csrftoken');
        }
        form.submit();
    }
    hideModal();
}


let renameCurrentDeviceId = null;

function showRenameModal(deviceId, currentName) {
    renameCurrentDeviceId = deviceId;
    document.getElementById('renameModalMessage').innerText =
        `Podaj nową nazwę dla urządzenia (ID: ${deviceId}):`;
    document.getElementById('newDeviceName').value = currentName;
    document.getElementById('renameError').innerText = '';
    document.getElementById('renameModal').style.display = "block";
}

document.getElementById('renameConfirmBtn').onclick = function () {
    if (renameCurrentDeviceId) {
        const newName = document.getElementById('newDeviceName').value.trim();
        fetch('/ajax_rename_device/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: 'device_id=' + encodeURIComponent(renameCurrentDeviceId) +
                  '&new_name=' + encodeURIComponent(newName)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                hideRenameModal();
                reloadDevicesList();
            } else {
                document.getElementById('renameError').innerText = data.error || 'nieznany błąd';
            }
        })
        .catch(() => {
            document.getElementById('renameError').innerText = 'Błąd połączenia z serwerem.';
        });
    }
};


function hideRenameModal() {
    document.getElementById('renameModal').style.display = "none";
    renameCurrentDeviceId = null;
    document.getElementById('renameError').innerText = '';
}

document.getElementById('confirmBtn').onclick = function() {
    if (currentDeviceId) {
        fetch('/ajax_delete_device/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: 'device_id=' + encodeURIComponent(currentDeviceId)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                reloadDevicesList();
            } else {
                alert('Nie udało się usunąć urządzenia: ' + (data.error || 'nieznany błąd'));
            }
        })
        .catch(() => alert('Błąd połączenia z serwerem.'));
    }
    hideModal();
}



// Zamykanie modali po kliknięciu w tło:
window.onclick = function(event) {
    // Obsługa modala usuwania
    let myModal = document.getElementById('myModal');
    if (myModal && event.target == myModal) {
        hideModal();
    }
    // Obsługa modala zmiany nazwy
    let renameModal = document.getElementById('renameModal');
    if (renameModal && event.target == renameModal) {
        hideRenameModal();
    }
}

// Zaznacz/odznacz wszystkie powiadomienia w tabeli powiadomień
document.addEventListener("DOMContentLoaded", function() {
    reloadDevicesList();
    reloadNotificationsTable();
    const selectAll = document.getElementById('select-all');
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('input[name="notification_ids"]');
            checkboxes.forEach(cb => cb.checked = selectAll.checked);
        });
    }
});

function reloadNotificationsTable() {
    saveSelectedNotifications();
    fetch('/notifications_table/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('notifications-table-container').innerHTML = data.html;
            restoreSelectedNotifications();
            const selectAll = document.getElementById('select-all');
            if (selectAll) {
                selectAll.addEventListener('change', function() {
                    const checkboxes = document.querySelectorAll('input[name="notification_ids"]');
                    checkboxes.forEach(cb => cb.checked = selectAll.checked);
                });
            }
        });
}
setInterval(reloadNotificationsTable, 10000); // Odświeżaj co 10 sekund

function reloadDevicesList() {
    fetch('/devices_list/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('devices-list');
            if (container) {
                container.innerHTML = data.html;
            }
        });
}
setInterval(reloadDevicesList, 10000); // Odświeżaj co 10 sekund

document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'delete-selected') {
        
        const checked = document.querySelectorAll('input[name="notification_ids"]:checked');
        const ids = Array.from(checked).map(cb => cb.value);
        if (ids.length === 0) {
            alert('Zaznacz powiadomienia do usunięcia.');
            return;
        }
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
    }
});

function saveSelectedNotifications() {
    selectedNotificationIds.clear();
    const checked = document.querySelectorAll('input[name="notification_ids"]:checked');
    checked.forEach(cb => selectedNotificationIds.add(cb.value));
}

function restoreSelectedNotifications() {
    const checkboxes = document.querySelectorAll('input[name="notification_ids"]');
    checkboxes.forEach(cb => {
        cb.checked = selectedNotificationIds.has(cb.value);
    });
}

