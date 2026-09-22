// AdvIT - User to User Chat Engine

function initChatThread(conversationId, currentUserId) {
  const messageList = document.getElementById('chatMessages');
  const messageInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSendBtn');
  const chatForm = document.getElementById('chatForm');

  if (!messageList || !chatForm) return;

  function scrollToBottom() {
    messageList.scrollTop = messageList.scrollHeight;
  }
  scrollToBottom();

  async function fetchNewMessages() {
    try {
      const res = await fetch(`/chat/conversations/${conversationId}/messages/`);
      if (res.ok) {
        const messages = await res.json();
        renderMessages(messages);
      }
    } catch (e) {
      console.error("Error polling messages:", e);
    }
  }

  function renderMessages(messages) {
    const isAtBottom = (messageList.scrollHeight - messageList.scrollTop) <= (messageList.clientHeight + 80);
    messageList.innerHTML = '';
    
    messages.forEach(msg => {
      const isMe = (msg.sender === currentUserId || msg.sender_id === currentUserId);
      const div = document.createElement('div');
      div.className = `d-flex mb-3 ${isMe ? 'justify-content-end' : 'justify-content-start'}`;
      
      div.innerHTML = `
        <div class="card p-3 shadow-sm ${isMe ? 'bg-primary text-white border-0' : 'bg-white text-dark'}" style="max-width: 75%; border-radius: 16px;">
          <div class="small fw-bold mb-1 opacity-75">${msg.sender_name || 'User'}</div>
          <div>${msg.content}</div>
          ${msg.attachment_url ? `<div class="mt-2"><a href="${msg.attachment_url}" target="_blank" class="badge bg-light text-dark text-decoration-none"><i class="bi bi-paperclip"></i> Attachment</a></div>` : ''}
          <div class="text-end mt-1" style="font-size: 0.7rem; opacity: 0.7;">${msg.formatted_time || ''}</div>
        </div>
      `;
      messageList.appendChild(div);
    });

    if (isAtBottom) {
      scrollToBottom();
    }
  }

  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const content = messageInput.value.trim();
    if (!content) return;

    messageInput.value = '';
    
    try {
      const res = await fetch(`/chat/conversations/${conversationId}/send/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({ content: content })
      });

      if (res.ok) {
        fetchNewMessages();
      }
    } catch (err) {
      console.error("Error sending message:", err);
    }
  });

  // Poll every 3 seconds for near-realtime chat
  setInterval(fetchNewMessages, 3000);
}
