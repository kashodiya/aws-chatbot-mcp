


class AWSChatbot {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.chatForm = document.getElementById('chat-form');
        this.sendBtn = document.getElementById('send-btn');
        this.clearBtn = document.getElementById('clear-chat');
        this.statusInfo = document.getElementById('status-info');
        
        this.init();
    }
    
    init() {
        // Event listeners
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.clearBtn.addEventListener('click', () => this.clearChat());
        
        // Example query buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const query = e.target.getAttribute('data-query');
                this.messageInput.value = query;
                this.messageInput.focus();
            });
        });
        
        // Auto-focus input
        this.messageInput.focus();
        
        // Check status
        this.checkStatus();
        
        // Auto-scroll to bottom
        this.scrollToBottom();
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Clear input and disable send button
        this.messageInput.value = '';
        this.setSendButtonState(false);
        
        // Add user message
        this.addMessage(message, 'user');
        
        // Add loading message
        const loadingId = this.addLoadingMessage();
        
        try {
            // Send message to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Remove loading message
            this.removeLoadingMessage(loadingId);
            
            if (data.success) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage(`Error: ${data.error}`, 'bot', 'error');
            }
            
        } catch (error) {
            // Remove loading message
            this.removeLoadingMessage(loadingId);
            this.addMessage(`Connection error: ${error.message}`, 'bot', 'error');
        }
        
        // Re-enable send button and focus input
        this.setSendButtonState(true);
        this.messageInput.focus();
    }
    
    addMessage(text, sender, type = 'normal') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fab fa-aws"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        
        if (type === 'error') {
            textDiv.style.background = '#dc3545';
            textDiv.style.color = 'white';
        }
        
        // Format message content
        textDiv.innerHTML = this.formatMessage(text);
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();
        
        content.appendChild(textDiv);
        content.appendChild(timeDiv);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    formatMessage(text) {
        // Convert newlines to <br>
        text = text.replace(/\n/g, '<br>');
        
        // Format code blocks (```code```)
        text = text.replace(/```([\s\S]*?)```/g, '<div class="code-block">$1</div>');
        
        // Format inline code (`code`)
        text = text.replace(/`([^`]+)`/g, '<code style="background: #f1f3f4; padding: 2px 4px; border-radius: 3px; font-family: monospace;">$1</code>');
        
        // Format AWS CLI commands
        text = text.replace(/(aws\s+[^\n<]+)/g, '<div class="code-block">$1</div>');
        
        return text;
    }
    
    addLoadingMessage() {
        const loadingId = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.id = loadingId;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fab fa-aws"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text loading-message';
        textDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Thinking<span class="loading-dots"></span></span>';
        
        content.appendChild(textDiv);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return loadingId;
    }
    
    removeLoadingMessage(loadingId) {
        const loadingMessage = document.getElementById(loadingId);
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
    
    setSendButtonState(enabled) {
        this.sendBtn.disabled = !enabled;
        if (enabled) {
            this.sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        } else {
            this.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }
    }
    
    clearChat() {
        // Keep only the welcome message
        const messages = this.chatMessages.querySelectorAll('.message');
        for (let i = 1; i < messages.length; i++) {
            messages[i].remove();
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    async checkStatus() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            let statusHtml = '';
            if (data.agent_available) {
                statusHtml = `
                    <div class="status-online">
                        <i class="fas fa-check-circle"></i> Agent Online
                    </div>
                    <small class="text-muted">
                        Region: ${data.settings.aws_region}<br>
                        Model: ${data.settings.model}<br>
                        Read-only: ${data.settings.read_only ? 'Yes' : 'No'}
                    </small>
                `;
            } else {
                statusHtml = `
                    <div class="status-offline">
                        <i class="fas fa-exclamation-circle"></i> Agent Offline
                    </div>
                    <small class="text-muted">Please check configuration</small>
                `;
            }
            
            this.statusInfo.innerHTML = statusHtml;
            
        } catch (error) {
            this.statusInfo.innerHTML = `
                <div class="status-offline">
                    <i class="fas fa-times-circle"></i> Connection Error
                </div>
                <small class="text-muted">${error.message}</small>
            `;
        }
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AWSChatbot();
});

// Handle Enter key in input
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey && document.activeElement.id === 'message-input') {
        e.preventDefault();
        document.getElementById('chat-form').dispatchEvent(new Event('submit'));
    }
});


