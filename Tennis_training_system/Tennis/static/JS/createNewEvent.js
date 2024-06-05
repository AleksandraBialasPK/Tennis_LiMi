const createNewEvent = document.querySelector(".create-new-event"),
     form = document.getElementById('form'),
    outsideOfForm = document.querySelector("main");

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
