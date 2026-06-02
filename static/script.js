/**
 * ================================================
 *  SmartBot — Frontend Chat Logic
 * ================================================
 *  Handles user input, API communication, and
 *  dynamic message rendering.
 * ================================================
 */

// --- DOM Elements ---
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const typingIndicator = document.getElementById('typingIndicator');

// --- Event Listeners ---
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
clearBtn.addEventListener('click', clearChat);

// --- Send Message ---
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    messageInput.focus();

    // Show typing indicator
    showTyping(true);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // Hide typing indicator
        showTyping(false);

        // Add bot response
        addMessage(data.response, 'bot', data.source);

    } catch (error) {
        showTyping(false);
        addMessage('Sorry, I could not connect to the server. Please make sure the server is running.', 'bot', 'error');
    }
}

// --- Send Suggestion (from chips) ---
function sendSuggestion(text) {
    messageInput.value = text;
    sendMessage();
}

// --- Add Message to Chat ---
function addMessage(text, sender, source = '') {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', `${sender}-message`);

    let avatarHTML = '';
    if (sender === 'bot') {
        avatarHTML = `
            <div class="msg-avatar">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2a4 4 0 0 1 4 4v2h1a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-6a3 3 0 0 1 3-3h1V6a4 4 0 0 1 4-4z"/>
                    <circle cx="9" cy="14" r="1.5" fill="currentColor"/>
                    <circle cx="15" cy="14" r="1.5" fill="currentColor"/>
                </svg>
            </div>`;
    }

    // Format text: convert **bold**, \n to <br>, and links
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');

    // Source badge
    let sourceHTML = '';
    if (source && source !== 'pattern' && source !== 'system') {
        const sourceLabels = {
            'wikipedia': 'Wikipedia',
            'web': 'Web Search',
            'error': 'Error'
        };
        const label = sourceLabels[source] || source;
        sourceHTML = `<span class="source-badge source-${source}">${label}</span>`;
    }

    messageDiv.innerHTML = `
        ${avatarHTML}
        <div class="msg-bubble">
            <p>${formattedText}</p>
            ${sourceHTML}
        </div>`;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// --- Typing Indicator ---
function showTyping(show) {
    if (show) {
        typingIndicator.classList.add('visible');
    } else {
        typingIndicator.classList.remove('visible');
    }
    scrollToBottom();
}

// --- Scroll to Bottom ---
function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 50);
}

// --- Clear Chat ---
function clearChat() {
    const messages = chatMessages.querySelectorAll('.message:not(.welcome-msg)');
    messages.forEach(msg => {
        msg.style.transition = 'all 0.3s ease';
        msg.style.opacity = '0';
        msg.style.transform = 'scale(0.9)';
        setTimeout(() => msg.remove(), 300);
    });
    messageInput.focus();
}
