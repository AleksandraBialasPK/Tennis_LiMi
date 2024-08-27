const createNewEvent = document.getElementById("create-new-game-button"),
    addNewCourt = document.getElementById("add-new-court-button"),
    addNewCategory = document.getElementById("create-new-category-button"),
    game_form = document.getElementById('game_form'),
    court_form = document.getElementById('court_form'),
    category_form = document.getElementById('category_form'),
    outsideOfForm = document.querySelector("main");


function toggleForm(form, button) {
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

function handleFormSubmission(form, successMessage, buttonName) {
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let formData = new FormData(this);

        formData.append(buttonName, 'true');

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

        // Event listener for recurrence type change
        $('#id_recurrence_type').change(function() {
            const recurrenceType = $(this).val();
            if (recurrenceType) {
                $('#recurrence-end-date').show();
            } else {
                $('#recurrence-end-date').hide();
                $('#id_end_date_of_recurrence').val('');
            }
        });

        // Initialize visibility based on the current selection
        const initialRecurrenceType = $('#id_recurrence_type').val();
        if (initialRecurrenceType) {
            $('#recurrence-end-date').show();
        } else {
            $('#recurrence-end-date').hide();
        }
    });
})(jQuery);