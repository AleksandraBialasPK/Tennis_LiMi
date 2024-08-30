let selectedDate;

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

    document.querySelectorAll('.checkbox-event').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            filterEvents();
        });
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

function updateEvents(data) {
    console.log("Received data:", data);
    const eventsDiv = document.getElementById("events");
    eventsDiv.innerHTML = '';

    if (Array.isArray(data.events)) {
        data.events.forEach(event => {
            appendEvent(event);
        });
    } else {
        console.error('No events found or data is not in expected format');
    }

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

function appendEvent(event) {
    const eventsDiv = document.getElementById("events");
    const eventDiv = document.createElement("div");

    eventDiv.className = `event-tile event-tile-${event.category__name}`;
    eventDiv.style.marginTop = `${event.margin_top}px`;
    eventDiv.style.height = `${event.height}px`;

    const profilePictureUrl = event.profile_picture_url;
    const categoryColor = event.category__color || '#ddd';
    const backgroundColorHEX = hexToRGBA(categoryColor, 0.3);

    eventDiv.style.backgroundColor = backgroundColorHEX;

    let editDeleteButtons = '';
        if (event.is_creator) {
            editDeleteButtons = `
                <button onclick="openEditForm(${event.game_id})" class="edit-button">
                    <i class="fa-solid fa-pen-to-square"></i>
                </button>
                
                <button onclick="deleteGame(${event.game_id})" class="delete-button">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            `;
        }

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
        ${editDeleteButtons}
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
    const checkboxes = document.querySelectorAll('.checkbox-event');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const color = this.getAttribute('data-color'); // Get the color from the data attribute
            if (this.checked) {
                this.style.backgroundColor = color;
                this.style.borderColor = color;
            } else {
                this.style.backgroundColor = 'rgba(0,0,0,0)';
                this.style.borderColor = '#ddd';
            }
        });

        checkbox.dispatchEvent(new Event('change'));
    });
});

function filterEvents() {
    const checkedCategories = Array.from(document.querySelectorAll('.checkbox-event:checked')).map(checkbox => checkbox.id);
    console.log('Checked Categories:', checkedCategories);

    const eventTiles = document.querySelectorAll('.event-tile');

    eventTiles.forEach(tile => {
        const categoryClass = Array.from(tile.classList).find(cls => cls.startsWith('event-tile-'));

        if (categoryClass) {
            const category = categoryClass.replace('event-tile-', '');
            console.log('Event Category:', category);

            if (checkedCategories.includes(category)) {
                tile.style.display = 'flex';
            } else {
                tile.style.display = 'none';
            }
        }
    });
}

// Function to open the form pre-filled for editing an event
function openEditForm(gameId) {
    const form = document.getElementById('game_form');
    form.setAttribute('data-game-id', gameId);
    form.style.display = 'block';
    console.log("Opening edit form for game ID:", gameId);

    // Set the game_id hidden field
    const gameIdField = form.querySelector('input[name="game_id"]');
    gameIdField.value = gameId;

    console.log("Setting hidden game_id field value:", gameIdField.value);

     // Show the update button, hide the add button
    document.getElementById('update-game-button').style.display = 'inline';
    document.getElementById('add-game-button').style.display = 'none';

    // Fetch current game details and populate the form
    $.ajax({
        url: `/day/`,
        method: 'GET',
        data: {
            'game_id': gameId, // Pass the game_id as a parameter to fetch details
            'fetch_game_details': 'true' // A flag to indicate this is a detail fetch request
        },
        success: function(data) {
            console.log("Game details loaded for editing:", data);
            form.querySelector('[name="name"]').value = data.name;
            form.querySelector('[name="start_date_and_time"]').value = data.start_date_and_time;
            form.querySelector('[name="end_date_and_time"]').value = data.end_date_and_time;
            form.querySelector('[name="category"]').value = data.category;
            form.querySelector('[name="court"]').value = data.court;

            const participantSelect = form.querySelector('[name="participants"]');
            if (participantSelect) {
                console.log("Setting participants:", data.participants);
                // Clear current selection
                $(participantSelect).val(null).trigger('change');

                // Loop through participants (email, username) tuples
                data.participants.forEach(participant => {
                    const email = participant[0];
                    const username = participant[1];
                    const displayText = `${username} (${email})`;

                    // Check if the option already exists
                    let option = $(participantSelect).find(`option[value="${email}"]`);
                    if (option.length) {
                        option.prop('selected', true);
                    } else {
                        // If the option is not found, add it as a new option
                        let newOption = new Option(displayText, email, true, true);
                        $(participantSelect).append(newOption).trigger('change');
                    }
                });

                // Trigger change event to update the Select2 component
                $(participantSelect).trigger('change');
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error('Failed to load game details:', textStatus, errorThrown);
            console.error('Response Text:', jqXHR.responseText);  // Print out the response text for debugging
            alert('Failed to load game details.');
        }
    });
}

function deleteGame(gameId) {
    console.log("Deleting game ID:", gameId);
    console.log("Using selectedDate:", selectedDate);
    if (confirm('Are you sure you want to delete this game?')) {
        $.ajax({
            url: `/day/`,
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            data: {
                'delete_game': 'true',
                'game_id': gameId
            },
            success: function(data) {
                if (data.success) {
                    alert('Game deleted successfully!');
                    loadEvents(selectedDate); // Reload events for the current date
                } else {
                    alert('Failed to delete game: ' + data.message);
                }
            },
            error: function() {
                alert('Failed to delete game.');
            }
        });
    }
}

const createNewEvent = document.getElementById("create-new-game-button"),
    addNewCourt = document.getElementById("add-new-court-button"),
    addNewCategory = document.getElementById("create-new-category-button"),
    game_form = document.getElementById('game_form'),
    court_form = document.getElementById('court_form'),
    category_form = document.getElementById('category_form'),
    outsideOfForm = document.querySelector("main");


function toggleForm(form, button, isEdit = false) {
    if (form && button) {
        form.style.display = 'none';
        button.addEventListener('click', () => {
            if (window.getComputedStyle(form).display === 'none') {

                form.style.display = 'block';
                outsideOfForm.addEventListener('click', function hideForm(event) {
                    if (!form.contains(event.target) && event.target !== button) {
                        form.style.display = 'none';
                        form.reset();
                        outsideOfForm.removeEventListener('click', hideForm);
                    }
                });
            } else {
                form.style.display = 'none';
                form.reset();
            }
        });
    } else {
        console.error(`Form or button element not found. Form ID: '${form ? form.id : "N/A"}', Button ID: '${button ? button.id : "N/A"}'`);
    }
}


toggleForm(game_form, createNewEvent);
toggleForm(court_form, addNewCourt);
toggleForm(category_form, addNewCategory);

const cancelEditButton = document.getElementById('cancel-edit');
if (cancelEditButton) {
    cancelEditButton.addEventListener('click', function () {
        if (confirm("Are you sure you want to cancel editing and discard changes?")) {
            game_form.reset();
            game_form.style.display = 'none';
        }
    });
} else {
    console.error('Cancel edit button not found');
}

function handleFormSubmission(form, successMessage, buttonName) {
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let formData = new FormData(this);

        formData.append(buttonName, 'true');

        const gameId = form.querySelector('[name="game_id"]').value;
        console.log("Form submission triggered. Game ID:", gameId);

        // Remove both flags first to avoid conflict
        formData.delete('submit_game');
        formData.delete('update_game');

        if (gameId) {
            console.log("Updating existing game with ID:", gameId);
            formData.append('update_game', 'true'); // Indicate update action
            formData.append('game_id', gameId); // Pass game_id for update
        } else {
            console.log("Creating a new game.");
            formData.append(buttonName, 'true'); // Normal submission for creating
        }

        // Print out all the form data for debugging
        formData.forEach((value, key) => {
            console.log(key, value);
        });

        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert(successMessage);
                form.reset();
                form.style.display = 'none';
                loadEvents(selectedDate);
            } else {
                if (data.errors) {
                    let errorMessages = '';
                    for (let field in data.errors) {
                        errorMessages += `${field}: ${data.errors[field].join(', ')}\n`;
                    }
                    alert('Failed: ' + errorMessages);
                } else {
                    alert('Failed: An unexpected error occurred.');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed: An unexpected error occurred.');
        });
    });
}

handleFormSubmission(document.getElementById('game_form'), 'Game added successfully!', 'submit_game');
handleFormSubmission(document.getElementById('court_form'), 'Court added successfully!', 'submit_court');
handleFormSubmission(document.getElementById('category_form'), 'Category added successfully!', 'submit_category');

(function($) {
    $(document).ready(function() {
        $('.django-select2').djangoSelect2();

        $('#id_recurrence_type').change(function() {
            const recurrenceType = $(this).val();
            if (recurrenceType) {
                $('#recurrence-end-date').show();
            } else {
                $('#recurrence-end-date').hide();
                $('#id_end_date_of_recurrence').val('');
            }
        });

        const initialRecurrenceType = $('#id_recurrence_type').val();
        if (initialRecurrenceType) {
            $('#recurrence-end-date').show();
        } else {
            $('#recurrence-end-date').hide();
        }
    });
})(jQuery);