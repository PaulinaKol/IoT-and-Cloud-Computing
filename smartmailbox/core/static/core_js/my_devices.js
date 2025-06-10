// Modal do usuwania urządzenia:
let currentDeviceId = null;

function showModal(deviceId) {
    currentDeviceId = deviceId;
    document.getElementById('modalMessage').innerText = `Czy napewno chcesz wyrejestrować urządzenie ${deviceId}?`;
    document.getElementById('myModal').style.display = "block";
}

function hideModal() {
    document.getElementById('myModal').style.display = "none";
    currentDeviceId = null;
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