document.addEventListener("DOMContentLoaded", function() {
    // Declare the selectedDate variable to store the current date being viewed
    let selectedDate = new Date().toISOString().split('T')[0];

    // Initial load for today's events using AJAX
    loadEvents(selectedDate);

    // Handle date navigation buttons
    document.querySelector('.prev-day-btn').addEventListener('click', function() {
        const date = this.getAttribute('data-date');
        selectedDate = date; // Update the selected date
        loadEvents(date);
    });

    document.querySelector('.next-day-btn').addEventListener('click', function() {
        const date = this.getAttribute('data-date');
        selectedDate = date; // Update the selected date
        loadEvents(date);
    });

    // Handle "Back to Today" button
    document.getElementById('back-to-today').addEventListener('click', function() {
        selectedDate = new Date().toISOString().split('T')[0]; // Reset to today's date
        loadEvents(selectedDate);
    });

    const intervalTime = 10000; // 10 seconds
    setInterval(function() {
        loadEvents(selectedDate); // Use the selected date
    }, intervalTime);
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

    eventDiv.className = `event-tile`;
    eventDiv.style.marginTop = `${event.margin_top}px`;
    eventDiv.style.height = `${event.height}px`;

    const profilePictureUrl = event.profile_picture_url;
    const categoryColor = event.category__color || '#ddd';
    const backgroundColor = hexToRGBA(categoryColor, 0.3);

    eventDiv.style.backgroundColor = backgroundColor;

    eventDiv.innerHTML = `
        <div class="side-color" style="background-color: ${categoryColor};">
            <div class="picture-for-event">
                <img src="${profilePictureUrl}" alt="User's Profile Picture">
            </div>
        </div>
        <div class="event-desc">
            <div class="event-name">${event.name}</div>
            <div class="event-time">${new Date(event.start_date_and_time).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})} - ${new Date(event.end_date_and_time).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</div>
        </div>
    `;

    eventsDiv.appendChild(eventDiv);
}

function hexToRGBA(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);

    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

document.addEventListener("DOMContentLoaded", function() {
    // Get all checkboxes with the class 'checkbox-event'
    const checkboxes = document.querySelectorAll('.checkbox-event');

    // Add event listener to each checkbox
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const color = this.getAttribute('data-color'); // Get the color from the data attribute
            if (this.checked) {
                // Apply the color when checked
                this.style.backgroundColor = color;
                this.style.borderColor = color;
            } else {
                // Revert to transparent when unchecked
                this.style.backgroundColor = 'rgba(0,0,0,0)';
                this.style.borderColor = '#ddd';
            }
        });

        // Trigger the change event on page load to set initial state
        checkbox.dispatchEvent(new Event('change'));
    });
});