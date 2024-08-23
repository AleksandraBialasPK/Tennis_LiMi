const createNewEvent = document.getElementById("create-new-event-button"),
    addNewCourt = document.getElementById("add-new-court-button"),
    addNewCategory = document.getElementById("create-new-category-button"),
    game_form = document.getElementById('game_form'),
    court_form = document.getElementById('court_form'),
    category_form = document.getElementById('category_form'),
    outsideOfForm = document.querySelector("main");

function toggleForm(form, button) {
    if (form) {
        form.style.display = 'none';
        button.addEventListener('click', () => {
            if (form.style.display === 'none') {
                form.style.display = 'block';
                outsideOfForm.addEventListener('click', function hideForm(event) {
                    if (!form.contains(event.target) && event.target !== button) {
                        form.style.display = 'none';
                        outsideOfForm.removeEventListener('click', hideForm);
                    }
                });
            } else {
                form.style.display = 'none';
            }
        });
    } else {
        console.error(`Element with ID '${form.id}' not found.`);
    }
}

toggleForm(game_form, createNewEvent);
toggleForm(court_form, addNewCourt);
toggleForm(category_form, addNewCategory);

function handleFormSubmission(form, successMessage) {
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let formData = new FormData(this);

        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(successMessage);
                form.reset();
            } else {
                alert('Failed: ' + JSON.stringify(data.errors));
            }
        })
        .catch(error => console.error('Error:', error));
    });
}

handleFormSubmission(game_form, 'Game added successfully!');
handleFormSubmission(court_form, 'Court added successfully!');
handleFormSubmission(category_form, 'Category added successfully!');
