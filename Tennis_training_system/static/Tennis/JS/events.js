document.addEventListener("DOMContentLoaded", function() {
    const ws = new WebSocket('ws://' + window.location.host + '/ws/events/');

    // Po nawiązaniu połączenia z serwerem, pobierz dane dla dzisiejszej daty
    ws.onopen = function() {
        const today = new Date().toISOString().split('T')[0]; // Pobierz bieżącą datę w formacie YYYY-MM-DD
        console.log('Połączenie WebSocket otwarte, żądanie wydarzeń dla:', today);
        ws.send(JSON.stringify({ date: today }));
    };

    ws.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log('Odebrane dane:', data);

        if (data.type === 'initial_event_load') {
            updateEvents(data);
        } else if (data.type === 'send_event_update') {
            appendEvent(data.event);
        }
    };

    ws.onclose = function(e) {
        console.error('Połączenie WebSocket niespodziewanie zamknięte');
    };

    ws.onerror = function(e) {
        console.error('Wystąpił błąd WebSocket');
    };

    // Aktualizacja daty i wydarzeń na stronie
    function updateEvents(data) {
        const eventsDiv = document.getElementById("events");
        eventsDiv.innerHTML = ''; // Wyczyść istniejące wydarzenia

        data.events.forEach(event => {
            appendEvent(event);
        });

        // Aktualizacja nawigacji po datach
        if (data.current_date && data.current_month && data.current_year) {
            document.getElementById('current-date').textContent = `${data.current_date} ${data.current_month} ${data.current_year}`;
        }
        if (data.prev_date) {
            document.querySelector('.prev-day-btn').setAttribute('data-date', data.prev_date);
        }
        if (data.next_date) {
            document.querySelector('.next-day-btn').setAttribute('data-date', data.next_date);
        }
    }

    function appendEvent(event) {
        const eventsDiv = document.getElementById("events");
        const eventDiv = document.createElement("div");

        // Set the appropriate classes and styles based on the event data
        eventDiv.className = `event-tile event-tile-${event.category__name}`;
        eventDiv.style.marginTop = `${event.margin_top}px`;
        eventDiv.style.height = `${event.height}px`;

        eventDiv.innerHTML = `
            <div class="side-color side-color-${event.category__name}">
                <div class="picture-for-event">
                    <img src="{% static 'images/Ola.png' %}" alt="user's profile picture"/>
                </div>
            </div>
            <div class="event-desc">
                <div class="event-name">${event.name}</div>
                <div class="event-time">${new Date(event.start_date_and_time).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})} - ${new Date(event.end_date_and_time).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</div>
            </div>
        `;

        eventsDiv.appendChild(eventDiv);
    }

    // Obsługa kliknięć przycisków do zmiany daty
    document.querySelector('.prev-day-btn').addEventListener('click', function() {
        const date = this.getAttribute('data-date');
        console.log('Żądanie wydarzeń dla poprzedniej daty:', date);
        ws.send(JSON.stringify({ date: date }));
    });

    document.querySelector('.next-day-btn').addEventListener('click', function() {
        const date = this.getAttribute('data-date');
        console.log('Żądanie wydarzeń dla następnej daty:', date);
        ws.send(JSON.stringify({ date: date }));
    });

    // Obsługa kliknięcia przycisku "Back to Today"
    document.getElementById('back-to-today').addEventListener('click', function() {
        const today = new Date().toISOString().split('T')[0];
        ws.send(JSON.stringify({ date: today }));
    });
});
