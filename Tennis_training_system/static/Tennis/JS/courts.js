document.addEventListener("DOMContentLoaded", function() {
    const addNewCourt = document.getElementById("add-new-court-button"),
        court_form = document.getElementById('court_form'),
        closeCourtFormButton = document.getElementById("closeCourtFormButton"),
        overlay = document.getElementById('overlay');

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

    // Apply form submission logic for court creation or update
    if (court_form) {
        handleFormSubmission(court_form, 'Court added/updated successfully!', 'submit_court');
    }

    const deleteButtons = document.querySelectorAll('.delete-court-button');  // Assuming each court has a delete button

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const courtId = this.dataset.courtId;  // Get court ID from data attribute
            if (confirm('Are you sure you want to delete this court?')) {
                const formData = new FormData();
                formData.append('delete_court', 'true');
                formData.append('court_id', courtId);

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
