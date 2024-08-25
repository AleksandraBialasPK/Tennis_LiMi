document.addEventListener("DOMContentLoaded", function() {
    const fileInput = document.getElementById('id_profile_picture');
    const avatarImage = document.getElementById('avatar-image');

    // Listen for changes on the file input
    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();

            reader.onload = function(e) {
                avatarImage.src = e.target.result;
                console.log("Profile picture updated in the preview.");
            };

            reader.readAsDataURL(file);
        } else {
            console.log("No file selected or file input change event not triggered.");
        }
    });
});