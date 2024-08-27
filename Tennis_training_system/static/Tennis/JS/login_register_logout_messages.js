document.addEventListener('DOMContentLoaded', function () {
    const messageContainer = document.getElementById('login-messages');

    function displayMessages(messages) {
        if (!messageContainer) {
            console.error('Message container not found.');
            return;
        }

        messageContainer.innerHTML = '';

        messages.forEach(message => {
            const li = document.createElement('li');
            li.className = message.tags;
            li.textContent = message.text;
            messageContainer.appendChild(li);
        });
    }
});
