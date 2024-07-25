const createNewEvent = document.querySelector(".create-new-event"),
      form = document.getElementById('game_form'),
      outsideOfForm = document.querySelector("main");
      categoryField = document.getElementById("id_category");
      trainerFieldDiv = document.getElementById("id_trainer-div");

if (form) {
    form.style.display = 'none';

    createNewEvent.addEventListener('click', () => {
        if (form.style.display === 'none') {
            form.style.display = 'block';
            outsideOfForm.addEventListener('click', () => {
                form.style.display = 'none';
            });
        } else {
            form.style.display = 'none';
        }
    });
} else {
    console.error("Element with ID 'form' not found.");
}

function checkCategory() {
    if (categoryField.options[categoryField.selectedIndex].text === "Training") {
        trainerFieldDiv.style.display = "block";
    } else {
        trainerFieldDiv.style.display = "none";
    }
}