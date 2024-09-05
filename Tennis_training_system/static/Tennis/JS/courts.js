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
});
