document.addEventListener("DOMContentLoaded", function() {
    fetch("/ajax_get_user_notification_settings/")
      .then(resp => resp.json())
      .then(data => {
          document.getElementById("notify_in").checked = data.notify_mail_in;
          document.getElementById("notify_out").checked = data.notify_mail_out;
          document.getElementById("notify_low_battery").checked = data.notify_low_battery;
          document.getElementById("notify_lost_connection").checked = data.notify_lost_connection;
      });

    document.getElementById("save-email-notifications").onclick = function() {
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== "") {
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
        const csrftoken = getCookie('csrftoken');
        fetch("/ajax_set_user_notification_settings/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrftoken,
            },
            body: new URLSearchParams({
                notify_mail_in: document.getElementById("notify_in").checked,
                notify_mail_out: document.getElementById("notify_out").checked,
                notify_low_battery: document.getElementById("notify_low_battery").checked,
                notify_lost_connection: document.getElementById("notify_lost_connection").checked,
            }),
        })
        .then(resp => resp.json())
        .then(data => {
            if (data.success) {
                const msg = document.getElementById("email-notification-message");
                msg.style.display = "block";
                setTimeout(() => {
                    msg.style.display = "none";
                }, 1500);
            }
        });
    };
});
