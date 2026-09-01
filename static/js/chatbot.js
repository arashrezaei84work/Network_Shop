document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('chatBotContainer');
    const toggle = document.getElementById('chatBotToggle');
    const windowChat = document.getElementById('chatBotWindow');
    const close = document.getElementById('chatClose');
    const input = document.getElementById('chatInput');
    const send = document.getElementById('chatSend');
    const body = document.getElementById('chatBody');

    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        windowChat.classList.toggle('open');
        container.classList.toggle('active');
    });

    close.addEventListener('click', (e) => {
        e.stopPropagation();
        windowChat.classList.remove('open');
        container.classList.remove('active');
    });

    function addMessage(text, type) {
        const div = document.createElement('div');
        div.className = type === 'user' ? 'user-message' : 'bot-message';
        div.innerHTML = `<p>${text}</p>`;
        body.appendChild(div);
        body.scrollTop = body.scrollHeight;
    }

    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        input.value = '';

        fetch("/chatbot-api/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
            body: JSON.stringify({ message: text })
        })
        .then(res => res.json())
        .then(data => addMessage(data.reply, 'bot'))
        .catch(() => addMessage("❌ خطا در ارتباط", 'bot'));
    }

    send.addEventListener('click', sendMessage);
    input.addEventListener('keydown', e => {
        if (e.key === 'Enter') sendMessage();
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(cookie => {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                }
            });
        }
        return cookieValue;
    }
});
