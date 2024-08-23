document.addEventListener("DOMContentLoaded", function() {
    // Initial load for today's events using AJAX
    const today = new Date().toISOString().split('T')[0];
    loadEvents(today);

    // Handle date navigation buttons
    document.querySelector('.prev-day-btn').addEventListener('click', function() {
        const date = this.getAttribute('data-date');
        loadEvents(date);
    });

    document.querySelector('.next-day-btn').addEventListener('click', function() {
        const date = this.getAttribute('data-date');
        loadEvents(date);
    });

    // Handle "Back to Today" button
    document.getElementById('back-to-today').addEventListener('click', function() {
        loadEvents(today);
    });
});

// Function to load events based on the given date
function loadEvents(date) {
    $.ajax({
        url: "/day/", // Ensure this URL matches your view handling the request
        data: { date: date },
        headers: {
            'x-requested-with': 'XMLHttpRequest' // This header is used to differentiate AJAX calls
        },
        success: function(data) {
            updateEvents(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
                    console.error('Failed to fetch events', textStatus, errorThrown);
                    console.error('Response Text:', jqXHR.responseText);  // Print out the response text for debugging
        }
    });
}

// Function to update the UI with the fetched events
function updateEvents(data) {
    console.log("Received data:", data);
    const eventsDiv = document.getElementById("events");
    eventsDiv.innerHTML = ''; // Clear existing events

    // Check if 'data.events' is an array
    if (Array.isArray(data.events)) {
        data.events.forEach(event => {
            appendEvent(event);
        });
    } else {
        console.error('No events found or data is not in expected format');
    }

    // Update date navigation
    if (data.current_date) {
        document.getElementById('current-date').textContent = data.current_date;
    }
    if (data.prev_date) {
        document.querySelector('.prev-day-btn').setAttribute('data-date', data.prev_date);
    }
    if (data.next_date) {
        document.querySelector('.next-day-btn').setAttribute('data-date', data.next_date);
    }
}

// Function to append a single event to the events container
function appendEvent(event) {
    const eventsDiv = document.getElementById("events");
    const eventDiv = document.createElement("div");

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
