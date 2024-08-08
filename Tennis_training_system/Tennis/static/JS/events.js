document.addEventListener("DOMContentLoaded", function() {
    const ws = new WebSocket('ws://' + window.location.host + '/ws/events/');

    ws.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'send_event_update') {
            const event = data.event;
            const eventsDiv = document.getElementById("events");
            const eventDiv = document.createElement("div");
            eventDiv.className = "event";
            eventDiv.style.top = event.margin_top + "%";
            eventDiv.style.height = event.height + "%";
            eventDiv.innerHTML = `
                <p>${event.name}</p>
                <p>${event.category}</p>
            `;
            eventsDiv.appendChild(eventDiv);
        }
    };

    ws.onclose = function(e) {
        console.error('WebSocket closed unexpectedly');
    };

    ws.onerror = function(e) {
        console.error('WebSocket error occurred');
    };
});