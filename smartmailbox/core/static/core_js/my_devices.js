// Modal do usuwania urządzenia:
let currentDeviceId = null;
let currentDeviceName = null;

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


document.getElementById('confirmBtn').onclick = function() {
    if (currentDeviceId) {
        document.getElementById(`delete-form-${currentDeviceId}`).submit();
    }
    hideModal();
}


// Modal do zmiany nazwy urządzenia:
let renameCurrentDeviceId = null;

function showRenameModal(deviceId, currentName) {
    renameCurrentDeviceId = deviceId;
    document.getElementById('renameModalMessage').innerText =
        `Podaj nową nazwę dla urządzenia (ID: ${deviceId}):`;
    document.getElementById('newDeviceName').value = currentName;
    document.getElementById('renameModal').style.display = "block";
}

function hideRenameModal() {
    document.getElementById('renameModal').style.display = "none";
    renameCurrentDeviceId = null;
}

document.getElementById('renameConfirmBtn').onclick = function () {
    if (renameCurrentDeviceId) {
        document.getElementById('renameDeviceId').value = renameCurrentDeviceId;
        document.getElementById('renameDeviceNewName').value =
            document.getElementById('newDeviceName').value.trim();
        document.getElementById('renameForm').submit();
    }
    hideRenameModal();
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
    const selectAll = document.getElementById('select-all');
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('input[name="notification_ids"]');
            checkboxes.forEach(cb => cb.checked = selectAll.checked);
        });
    }
});

function reloadNotificationsTable() {
    fetch('/notifications_table/')
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('notifications-table');
            if (table) {
                table.innerHTML = data.html;
            }
            // Ponownie podpinamy event zaznaczania wszystkich po podmianie DOM
            const selectAll = document.getElementById('select-all');
            if (selectAll) {
                selectAll.addEventListener('change', function() {
                    const checkboxes = document.querySelectorAll('input[name="notification_ids"]');
                    checkboxes.forEach(cb => cb.checked = selectAll.checked);
                });
            }
        });
}
setInterval(reloadNotificationsTable, 10000); // Odświeżaj co 10 sekund:

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
setInterval(reloadDevicesList, 10000); // Odświeżaj co 10 sekund: