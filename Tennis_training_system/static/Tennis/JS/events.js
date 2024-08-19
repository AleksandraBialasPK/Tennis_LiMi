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

    // Dodanie pojedynczego wydarzenia do kontenera wydarzeń
    function appendEvent(event) {
        const eventsDiv = document.getElementById("events");
        const eventDiv = document.createElement("div");
        eventDiv.className = "event";
        eventDiv.innerHTML = `
            <p>${event.name}</p>
            <p>${event.category__name}</p>
            <p>${new Date(event.start_date_and_time).toLocaleString()} - ${new Date(event.end_date_and_time).toLocaleString()}</p>
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
});
