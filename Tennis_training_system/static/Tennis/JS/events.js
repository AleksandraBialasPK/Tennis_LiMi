let selectedDate;

document.addEventListener("DOMContentLoaded", function() {
    let selectedDate = new Date().toISOString().split('T')[0];

    loadEvents(selectedDate);

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

    document.getElementById('back-to-today').addEventListener('click', function() {
        selectedDate = new Date().toISOString().split('T')[0]; // Reset to today's date
        loadEvents(selectedDate);
    });

    document.querySelectorAll('.checkbox-event').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            filterEvents();
        });
    });

    const intervalTime = 10000;
    setInterval(function() {
        loadEvents(selectedDate);
    }, intervalTime);
});

function loadEvents(date) {
    $.ajax({
        url: "/day/",
        data: { date: date },
        headers: {
            'x-requested-with': 'XMLHttpRequest'
        },
        success: function(data) {
            updateEvents(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
                    console.error('Failed to fetch events', textStatus, errorThrown);
                    console.error('Response Text:', jqXHR.responseText);
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

    const warningIcon = event.warning ? `<i class="fa-solid fa-road-circle-exclamation" style="color: crimson; margin-right: 5px;"></i>` : '';

    eventDiv.innerHTML = `
        <div class="side-color" style="background-color: ${categoryColor};">
            <div class="picture-for-event">
                <img src="${profilePictureUrl}" alt="User's Profile Picture">
            </div>
        </div>
        <div class="event-desc">
            <div class="event-name">${warningIcon}${event.name}</div>
            <div class="event-time">${new Date(event.start_date_and_time).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})} - ${new Date(event.end_date_and_time).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</div>
        </div>
    `;
        
    eventDiv.addEventListener('click', function() {
        showEventDetails(event);
    });

    eventsDiv.appendChild(eventDiv);
}

function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);

    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${day}.${month}.${year}, ${hours}:${minutes}`;
}

function showEventDetails(gameId) {
    console.log("Fetching details for game:", gameId);
    const gameIdData = gameId.game_id;

    $.ajax({
        url: `/day/`,
        method: 'GET',
        data: {
            'game_id': gameIdData,
            'fetch_game_details': 'true'
        },
        success: function(data) {
            console.log("Game details loaded for presenting:", data);

            const modal = document.getElementById('eventDetailsModal');

            modal.querySelector('.modal-title').textContent = data.name;
            modal.querySelector('.modal-start-time').textContent = `Start: ${formatDateTime(data.start_date_and_time)}`;
            modal.querySelector('.modal-end-time').textContent = `End: ${formatDateTime(data.end_date_and_time)}`;
            modal.querySelector('.modal-category').textContent = `Category: ${data.category_name}`;
            modal.querySelector('.modal-court').textContent = `Court: ${data.court_name}`;

            const participantsList = modal.querySelector('.modal-participants-list');
            participantsList.innerHTML = ''; // Clear existing list items

            // Add each participant to the list
            data.participants.forEach(participant => {
                const email = participant[0];
                const username = participant[1];
                const listItem = document.createElement('li');
                listItem.textContent = `${username} (${email})`;
                participantsList.appendChild(listItem);
            });

            const editButton = modal.querySelector('.edit-button');
            const deleteButton = modal.querySelector('.delete-button');

            if (data.is_creator) {
                // Show edit and delete buttons if the user is the creator
                editButton.style.display = 'inline-block';
                deleteButton.style.display = 'inline-block';

                // Set up click handlers
                editButton.addEventListener('click', function() {
                    openEditForm(gameIdData);
                });

                deleteButton.addEventListener('click', function() {
                    deleteGame(gameIdData);
                });
            } else {
                // Hide buttons if the user is not the creator
                editButton.style.display = 'none';
                deleteButton.style.display = 'none';
            }

            modal.style.display = 'block';

            const closeModalButton = document.getElementById('closeModalButton');
            closeModalButton.addEventListener('click', function() {
                modal.style.display = 'none';
            });
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error('Failed to load game details:', textStatus, errorThrown);
            console.error('Response Text:', jqXHR.responseText);
            alert('Failed to load game details.');
        }
    });
}

window.onclick = function(event) {
    const modal = document.getElementById('eventDetailsModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

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
            const color = this.getAttribute('data-color');
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

function openEditForm(gameId) {
    const form = document.getElementById('game_form');
    form.setAttribute('data-game-id', gameId);
    form.style.display = 'block';
    console.log("Opening edit form for game ID:", gameId);

    const gameIdField = form.querySelector('input[name="game_id"]');
    gameIdField.value = gameId;

    console.log("Setting hidden game_id field value:", gameIdField.value);

    document.getElementById('update-game-button').style.display = 'inline';
    document.getElementById('add-game-button').style.display = 'none';

    $.ajax({
        url: `/day/`,
        method: 'GET',
        data: {
            'game_id': gameId,
            'fetch_game_details': 'true'
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
                $(participantSelect).val(null).trigger('change');

                data.participants.forEach(participant => {
                    const email = participant[0];
                    const username = participant[1];
                    const displayText = `${username} (${email})`;

                    let option = $(participantSelect).find(`option[value="${email}"]`);
                    if (option.length) {
                        option.prop('selected', true);
                    } else {
                        let newOption = new Option(displayText, email, true, true);
                        $(participantSelect).append(newOption).trigger('change');
                    }
                });

                $(participantSelect).trigger('change');
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.error('Failed to load game details:', textStatus, errorThrown);
            console.error('Response Text:', jqXHR.responseText);
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
                        const select2Fields = gameForm.querySelectorAll('.django-select2');
                        select2Fields.forEach(field => {
                        $(field).val(null).trigger('change'); // Reset the select2 field
                        });
                        outsideOfForm.removeEventListener('click', hideForm);
                    }
                });
            } else {
                form.style.display = 'none';
                form.reset();
                const select2Fields = gameForm.querySelectorAll('.django-select2');
                select2Fields.forEach(field => {
                    $(field).val(null).trigger('change'); // Reset the select2 field
                });
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
            const select2Fields = gameForm.querySelectorAll('.django-select2');
            select2Fields.forEach(field => {
                $(field).val(null).trigger('change'); // Reset the select2 field
            });
            game_form.style.display = 'none';
        }
    });
} else {
    console.error('Cancel edit button not found');
}

function handleFormSubmission(form, successMessage, buttonName) {
    const modal = document.getElementById('confirmationModal');
    const modalMessage = document.getElementById('modalMessage');
    const confirmYes = document.getElementById('confirmYes');
    const confirmNo = document.getElementById('confirmNo');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let formData = new FormData(this);

        formData.append(buttonName, 'true');

        const isGameForm = (buttonName === 'submit_game' || buttonName === 'update_game');

        if(isGameForm) {
            const gameId = form.querySelector('[name="game_id"]').value;

            formData.delete('submit_game');
            formData.delete('update_game');

            if (gameId) {
                formData.append('update_game', 'true');
                formData.append('game_id', gameId);
            } else {
                formData.append(buttonName, 'true');
            }
        } else {
            formData.append(buttonName, 'true');
        }

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
                const select2Fields = form.querySelectorAll('.django-select2');
                select2Fields.forEach(field => {
                    $(field).val(null).trigger('change'); // Reset the select2 field
                });
                form.style.display = 'none';
                loadEvents(selectedDate);
            } else if (data.confirm_needed) {
                // Show custom modal with the warning message
                modalMessage.textContent = data.message;
                modal.style.display = 'block';

                // Yes button: User wants to add the game anyway
                confirmYes.onclick = function() {
                    modal.style.display = 'none';
                    formData.append('confirm', 'true');

                    // Re-send the form with the confirmation flag
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
                            const select2Fields = form.querySelectorAll('.django-select2');
                            select2Fields.forEach(field => {
                                $(field).val(null).trigger('change'); // Reset the select2 field
                            });
                            form.style.display = 'none';
                            loadEvents(selectedDate);
                        } else {
                            alert('Failed to add game: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Failed: An unexpected error occurred.');
                    });
                };

                // No button: User cancels the action
                confirmNo.onclick = function() {
                    modal.style.display = 'none';
                };
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