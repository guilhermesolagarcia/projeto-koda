const CRISIS_KEYWORDS = [
  'suicídio', 'suicidio', 'me matar', 'quero morrer', 
  'não quero mais viver', 'nao quero mais viver', 
  'me machucar', 'automutilação', 'automutilaçao', 
  'desaparecer', 'fim da minha vida'
];

let historico = [];
let isLoading = false;
let editingIndex = null; // Variável nova para controlar se estamos editando

document.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('koda_historico');
  if (saved) {
    historico = JSON.parse(saved);
    historico.forEach((msg, index) => {
      if (msg.role !== 'system') {
        renderMessage(msg.content, msg.role === 'user' ? 'user' : 'koda', index);
      }
    });
    if (historico.length > 0) {
      document.getElementById('welcome').style.display = 'none';
    }
  }

  const theme = localStorage.getItem('koda_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', theme);
  updateThemeIcon(theme);

  const input = document.getElementById('userInput');
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 150) + 'px';
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
});

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('koda_theme', next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const btn = document.querySelector('.theme-toggle');
  btn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

function saveHistorico() {
  localStorage.setItem('koda_historico', JSON.stringify(historico));
}

function clearChat() {
  if (!confirm('Tem certeza que deseja apagar toda a conversa?')) return;
  historico = [];
  localStorage.removeItem('koda_historico');
  cancelEdit(); // Se apagar o chat, cancela qualquer edição ativa
  const msgs = document.getElementById('messages');
  msgs.innerHTML = `
    <div class="welcome" id="welcome">
      <div class="welcome-icon">K</div>
      <h2>Olá, eu sou o KODA</h2>
      <p>Este é o seu espaço seguro. Estou aqui para te ouvir, sem julgamentos, a qualquer hora do dia ou da noite.</p>
      <div class="welcome-chips">
        <button class="chip" onclick="sendChip(this)">Preciso desabafar</button>
        <button class="chip" onclick="sendChip(this)">Tô com muita ansiedade</button>
        <button class="chip" onclick="sendChip(this)">Me sinto sozinho hoje</button>
        <button class="chip" onclick="sendChip(this)">Quero um conselho</button>
      </div>
    </div>`;
  document.getElementById('crisisBanner').classList.remove('visible');
}

function checkCrisis(text) {
  const lower = text.toLowerCase();
  return CRISIS_KEYWORDS.some(kw => lower.includes(kw));
}

function getTime() {
  return new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

// -----------------------------------------------------
// RENDERIZAÇÃO
// -----------------------------------------------------
function renderMessage(text, role, index = null) {
  const welcome = document.getElementById('welcome');
  if (welcome) welcome.style.display = 'none';

  const msgs = document.getElementById('messages');
  const msg = document.createElement('div');
  msg.className = `message ${role}`;
  if (index !== null) msg.dataset.index = index;

  const avatar = role === 'koda'
    ? `<div class="msg-avatar">K</div>`
    : `<div class="msg-avatar user-av">US</div>`;

  let formattedContent = "";
  if (role === 'koda') {
    if (typeof marked !== 'undefined') {
      marked.setOptions({ breaks: true });
      formattedContent = marked.parse(text);
    } else {
      formattedContent = text.replace(/\n/g, '<br>');
    }
  } else {
    formattedContent = text.split('\n').filter(p => p.trim() !== '').map(p => `<p>${p}</p>`).join('');
  }

  let actionButtons = '';
  const copyIcon = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
  const editIcon = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>`;
  const redoIcon = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>`;
  
  if (role === 'user' && index !== null) {
    actionButtons = `
      <div class="msg-actions">
        <button class="action-btn" title="Copiar mensagem" onclick="copyMessage(this)">${copyIcon}</button>
        <button class="action-btn" title="Editar mensagem" onclick="editMessage(${index})">${editIcon}</button>
      </div>`;
  } else if (role === 'koda' && index !== null) {
    actionButtons = `
      <div class="msg-actions">
        <button class="action-btn" title="Copiar resposta" onclick="copyMessage(this)">${copyIcon}</button>
        <button class="action-btn" title="Refazer resposta" onclick="redoMessage(${index})">${redoIcon}</button>
      </div>`;
  }

  msg.innerHTML = `
    ${avatar}
    <div class="msg-wrapper">
      <div class="bubble">${formattedContent}</div>
      ${actionButtons}
      <div class="msg-time">${getTime()}</div>
    </div>`;

  msgs.appendChild(msg);
  msgs.scrollTop = msgs.scrollHeight;
}

function renderTyping() {
  const msgs = document.getElementById('messages');
  const el = document.createElement('div');
  el.className = 'message koda';
  el.id = 'typing';
  el.innerHTML = `
    <div class="msg-avatar">K</div>
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>`;
  msgs.appendChild(el);
  msgs.scrollTop = msgs.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById('typing');
  if (el) el.remove();
}

// -----------------------------------------------------
// FUNÇÕES DOS BOTÕES E EDIÇÃO (Com Fallback para Celular)
// -----------------------------------------------------
function copyMessage(btnElement) {
  const bubble = btnElement.closest('.msg-wrapper').querySelector('.bubble');
  const textToCopy = bubble.innerText;

  const showSuccess = () => {
    const originalHTML = btnElement.innerHTML;
    btnElement.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    setTimeout(() => { btnElement.innerHTML = originalHTML; }, 2000);
  };

  // Tenta usar a API moderna (funciona no PC ou com HTTPS)
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(textToCopy).then(showSuccess);
  } else {
    // PLANO B: Hack antigo que dribla o bloqueio do celular
    const textArea = document.createElement("textarea");
    textArea.value = textToCopy;
    textArea.style.position = "fixed"; // Evita que a tela pule
    textArea.style.left = "-9999px";
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      showSuccess();
    } catch (err) {
      console.error('Erro ao copiar no celular', err);
    }
    document.body.removeChild(textArea);
  }
}

// Inicia o Modo de Edição (Não apaga nada ainda!)
function editMessage(index) {
  editingIndex = index;
  const msgToEdit = historico[index].content;
  const input = document.getElementById('userInput');
  
  input.value = msgToEdit;
  input.focus();
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 150) + 'px';
  
  // Mostra o aviso que estamos editando
  document.getElementById('editBanner').style.display = 'flex';
}

// Cancela o Modo de Edição
function cancelEdit() {
  editingIndex = null;
  const input = document.getElementById('userInput');
  input.value = '';
  input.style.height = 'auto';
  document.getElementById('editBanner').style.display = 'none';
}

async function redoMessage(index) {
  if (isLoading) return;
  historico = historico.slice(0, index - 1);
  const lastUserText = JSON.parse(localStorage.getItem('koda_historico'))[index - 1].content;
  saveHistorico();
  reloadChatUI();
  document.getElementById('userInput').value = lastUserText;
  sendMessage();
}

function reloadChatUI() {
  const msgs = document.getElementById('messages');
  msgs.innerHTML = `
    <div class="welcome" id="welcome" style="display: none;"></div>`;
  historico.forEach((msg, i) => {
    renderMessage(msg.content, msg.role === 'user' ? 'user' : 'koda', i);
  });
}

// -----------------------------------------------------
// ENVIO DE MENSAGEM API
// -----------------------------------------------------
function sendChip(el) {
  document.getElementById('userInput').value = el.textContent;
  sendMessage();
}

async function sendMessage() {
  const input = document.getElementById('userInput');
  const text = input.value.trim();
  const sendBtn = document.getElementById('sendBtn');
  
  if (!text || isLoading) return;

  // VERIFICA SE É UMA MENSAGEM NOVA OU UMA EDIÇÃO CONCLUÍDA
  if (editingIndex !== null) {
    historico = historico.slice(0, editingIndex); // Agora sim a gente corta o histórico antigo!
    editingIndex = null;
    document.getElementById('editBanner').style.display = 'none';
    reloadChatUI(); // Limpa as mensagens velhas da tela
  }

  input.value = '';
  input.style.height = 'auto';
  isLoading = true;
  sendBtn.disabled = true;

  historico.push({ role: 'user', content: text });
  renderMessage(text, 'user', historico.length - 1);

  if (checkCrisis(text)) {
    document.getElementById('crisisBanner').classList.add('visible');
  }

  renderTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mensagem: text, historico: historico.slice(0, -1) })
    });

    const data = await res.json();
    removeTyping();
    historico.push({ role: 'assistant', content: data.resposta });
    renderMessage(data.resposta, 'koda', historico.length - 1);
    saveHistorico();

  } catch (err) {
    removeTyping();
    renderMessage('Desculpe, tive um problema de conexão agora. Pode tentar enviar de novo?', 'koda', null);
  }

  isLoading = false;
  sendBtn.disabled = false;
  input.focus();
}