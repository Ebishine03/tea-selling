// WebSocket connection and notification handling
//
let notificationSocket;

function connectWebSocket() {
    notificationSocket = new WebSocket(`ws://${window.location.host}/ws/notifications/${userId}/`);

    notificationSocket.onopen = () => console.log("WebSocket connected");

    notificationSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('Notification received:', data.message);

        // Dynamically display the new notification
        displayNotification(data);

        // Update unread badge count if available
        const unreadBadge = document.querySelector('.badge-number');
        if (unreadBadge) {
            let unreadCount = parseInt(unreadBadge.innerText) + 1;
            unreadBadge.innerText = unreadCount;
        }
    };

    notificationSocket.onclose = () => {
        console.error("WebSocket closed. Attempting to reconnect...");
        setTimeout(connectWebSocket, 3000);  // Reconnect after 3 seconds
    };

    notificationSocket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

function displayNotification(notification) {
    const notificationList = document.getElementById('notification-list');
    const notificationItem = document.createElement('li');
    notificationItem.className = 'notification-item unread';
    notificationItem.innerHTML = `
        <span>${notification.message}</span>
        <button class="mark-as-read" data-id="${notification.id}">Mark as Read</button>
    `;
    notificationList.prepend(notificationItem);

    // Attach mark as read event
    notificationItem.querySelector('.mark-as-read').addEventListener('click', markAsRead);
}

function markAsRead(event) {
    event.preventDefault();
    const button = event.target;
    const notificationId = button.getAttribute('data-id');

    // Send request to mark notification as read
    notificationSocket.send(JSON.stringify({ 'notification_id': notificationId }));

    // Update the UI to reflect the read status
    button.closest('.notification-item').classList.add('read');
    button.remove();

    // Update unread badge count
    const unreadBadge = document.querySelector('.badge-number');
    if (unreadBadge) {
        let unreadCount = parseInt(unreadBadge.innerText) - 1;
        unreadBadge.innerText = unreadCount > 0 ? unreadCount : '';
    }
}

connectWebSocket(userId)