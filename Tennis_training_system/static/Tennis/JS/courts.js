document.addEventListener("DOMContentLoaded", function() {
    const addNewCourt = document.getElementById("add-new-court-button"),
        court_form = document.getElementById('court_form'),
        closeCourtFormButton = document.getElementById("closeCourtFormButton"),
        overlay = document.getElementById('overlay'),
        editButtons = document.querySelectorAll('.edit-button'),
        updateCourtButton = document.querySelector('button[name="update_court"]'),
        addCourtButton = document.querySelector('button[name="submit_court"]');

    // Function to hide the form and overlay
    function hideForm(form) {
        if (form) {
            form.style.display = 'none';
        }
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    // Function to show the form and overlay
    function showForm(form) {
        if (form) {
            form.style.display = 'block';
        }
        if (overlay) {
            overlay.style.display = 'block';
        }
    }

    // Function to toggle the form display
    function toggleForm(form, button) {
        button.addEventListener('click', function() {
            if (window.getComputedStyle(form).display === 'none') {
                // Show the form if it's currently hidden
                showForm(form);
            } else {
                // Hide the form if it's currently visible
                hideForm(form);
                form.reset(); // Reset the form when hiding
            }
        });
    }

    // Close form when the close button is clicked
    if (closeCourtFormButton) {
        closeCourtFormButton.addEventListener('click', function() {
            hideForm(court_form);
            court_form.reset();
        });
    }

    // Initialize the form toggle on the "Add New Court" button
    if (court_form && addNewCourt) {
        // Ensure form is hidden on page load
        hideForm(court_form);
        toggleForm(court_form, addNewCourt);
    } else {
        console.error('Add New Court button or court form not found in the DOM');
    }

    function handleFormSubmission(form, successMessage, buttonName) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();  // Prevent default form submission behavior
            let formData = new FormData(this);  // Collect form data
            formData.append(buttonName, 'true');  // Append the button name (submit_court/update_court)

            // Send the form data using fetch to handle submission
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,  // Django CSRF protection
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        alert(successMessage);  // Show success message
                        form.reset();  // Reset the form fields
                        form.style.display = 'none';
                        if (overlay) overlay.style.display = 'none';
                    } else {
                        // Handle validation errors
                        let errorMessages = '';
                        for (let field in data.errors) {
                            errorMessages += `${field}: ${data.errors[field].join(', ')}\n`;
                        }
                        alert('Failed: ' + errorMessages);  // Show error messages
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Failed: An unexpected error occurred.');
                });
        });
    }

    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const courtId = this.closest('.court-item').querySelector('.delete-button').dataset.courtId;

            // Use fetch to get court data and populate form for editing via POST request
            const formData = new FormData();
            formData.append('fetch_court_data', 'true');
            formData.append('court_id', courtId);

            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Populate the form with court details for editing
                court_form.querySelector('input[name="court_id"]').value = courtId;
                court_form.querySelector('input[name="name"]').value = data.name;
                court_form.querySelector('input[name="building_number"]').value = data.building_number;
                court_form.querySelector('input[name="street"]').value = data.street;
                court_form.querySelector('input[name="city"]').value = data.city;
                court_form.querySelector('input[name="postal_code"]').value = data.postal_code;
                court_form.querySelector('input[name="country"]').value = data.country;

                // Switch form buttons to show "Update" instead of "Add"
                updateCourtButton.style.display = 'inline';
                addCourtButton.style.display = 'none';

                court_form.style.display = 'block';
                overlay.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching court data:', error);
                alert('Failed to load court data for editing.');
            });
        });
    });

    closeCourtFormButton.addEventListener('click', function() {
        court_form.reset();
        court_form.querySelector('input[name="court_id"]').value = '';  // Reset court_id for new court creation
        updateCourtButton.style.display = 'none';
        addCourtButton.style.display = 'inline';
        court_form.style.display = 'none';
        overlay.style.display = 'none';
    });

    // Apply form submission logic for court creation or update
    if (court_form) {
        handleFormSubmission(court_form, 'Court added/updated successfully!', 'submit_court');
    }

    const deleteButtons = document.querySelectorAll('.delete-button');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const courtId = this.dataset.courtId;  // Get court ID from data attribute
            if (confirm('Are you sure you want to delete this court?')) {
                const formData = new FormData();
                formData.append('delete_court', 'true');
                formData.append('court_id', courtId);

                // Get CSRF token from the cookie or hidden input
                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

                fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,  // Ensure the CSRF token is passed here
                        'X-Requested-With': 'XMLHttpRequest'  // Identify as an AJAX request
                    },
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        alert(data.message);  // Show success message
                        location.reload();  // Optionally reload the page or update the DOM dynamically
                    } else {
                        alert('Failed: ' + data.message);  // Show failure message
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Failed: An unexpected error occurred.');
                });
            }
        });
    });
});
