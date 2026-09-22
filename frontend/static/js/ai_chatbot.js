// AdvIT - AI Chatbot Global Widget Logic

document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('aiChatWidgetBtn');
  const panel = document.getElementById('aiChatWidgetPanel');
  const closeBtn = document.getElementById('aiChatCloseBtn');
  const input = document.getElementById('aiChatInput');
  const sendBtn = document.getElementById('aiChatSendBtn');
  const msgContainer = document.getElementById('aiChatMessages');

  if (!toggleBtn || !panel) return;

  let sessionId = localStorage.getItem('advit_ai_session') || '';
  if (!sessionId) {
    sessionId = 'sess_' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('advit_ai_session', sessionId);
  }

  toggleBtn.addEventListener('click', () => {
    if (panel.style.display === 'flex') {
      panel.style.display = 'none';
    } else {
      panel.style.display = 'flex';
      input.focus();
    }
  });

  closeBtn.addEventListener('click', () => {
    panel.style.display = 'none';
  });

  function appendMessage(text, role, structuredData = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `ai-msg ai-msg-${role}`;
    
    // Parse markdown / link formatting simply
    let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formattedText = formattedText.replace(/\n/g, '<br>');
    msgDiv.innerHTML = formattedText;

    if (structuredData && structuredData.team_recommendations) {
      const recs = structuredData.team_recommendations;
      let cardHtml = `<div class="mt-2 p-2 bg-light rounded text-dark border">
        <h6 class="mb-1 text-primary fw-bold"><i class="bi bi-people-fill"></i> Suggested Team Roles:</h6>`;
      recs.forEach(r => {
        cardHtml += `<div class="small mb-1">• <strong>${r.role}</strong>: <span class="text-muted">${r.description || ''}</span></div>`;
      });
      cardHtml += `</div>`;
      msgDiv.innerHTML += cardHtml;
    }

    msgContainer.appendChild(msgDiv);
    msgContainer.scrollTop = msgContainer.scrollHeight;
  }

  async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    appendMessage(message, 'user');
    input.value = '';
    input.disabled = true;
    sendBtn.disabled = true;

    // Loading bubble
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'ai-msg ai-msg-assistant loading-indicator text-muted';
    loadingDiv.innerHTML = '<span class="spinner-grow spinner-grow-sm" role="status"></span> Thinking...';
    msgContainer.appendChild(loadingDiv);
    msgContainer.scrollTop = msgContainer.scrollHeight;

    try {
      const response = await fetch('/ai/api/chatbot/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        })
      });

      const data = await response.json();
      loadingDiv.remove();

      if (response.ok && data.reply) {
        appendMessage(data.reply, 'assistant', data.structured_data);
      } else {
        appendMessage(data.error || "I'm having trouble connecting right now. Please try again!", 'assistant');
      }
    } catch (err) {
      loadingDiv.remove();
      appendMessage("Unable to reach the AdvIT AI Assistant. Please check your connection.", 'assistant');
    } finally {
      input.disabled = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
});
