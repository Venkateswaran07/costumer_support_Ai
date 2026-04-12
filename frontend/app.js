/* ============================================
   NEXUS AI — APPLICATION LOGIC
   ============================================ */

// --- State ---
const API_URL = "https://costumer-support-ai.onrender.com/chat";
const userId = "user_" + Math.random().toString(36).substring(2, 9);

let conversations = JSON.parse(localStorage.getItem("nexus_conversations") || "[]");
let activeConversationId = null;
let isWaiting = false;

// --- DOM References ---
const messagesContainer = document.getElementById("messagesContainer");
const chatMessages = document.getElementById("chatMessages");
const welcomeScreen = document.getElementById("welcomeScreen");
const typingIndicator = document.getElementById("typingIndicator");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const charCount = document.getElementById("charCount");
const chatTitle = document.getElementById("chatTitle");
const conversationsList = document.getElementById("conversationsList");
const themeToggle = document.getElementById("themeToggle");
const themeLabel = document.getElementById("themeLabel");
const newChatBtn = document.getElementById("newChatBtn");
const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebarToggle");
const sidebarOverlay = document.getElementById("sidebarOverlay");
const searchInput = document.getElementById("searchInput");

// ============================================
//  THEME MANAGEMENT
// ============================================
function initTheme() {
    const saved = localStorage.getItem("nexus_theme") || "dark";
    document.documentElement.setAttribute("data-theme", saved);
    updateThemeLabel(saved);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("nexus_theme", next);
    updateThemeLabel(next);
}

function updateThemeLabel(theme) {
    themeLabel.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
}

themeToggle.addEventListener("click", toggleTheme);
initTheme();

// ============================================
//  SIDEBAR (Mobile)
// ============================================
sidebarToggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    sidebarOverlay.classList.toggle("active");
});

sidebarOverlay.addEventListener("click", () => {
    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("active");
});

// ============================================
//  TEXTAREA AUTO-RESIZE
// ============================================
messageInput.addEventListener("input", () => {
    // Auto-resize
    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + "px";

    // Char count
    const len = messageInput.value.length;
    charCount.textContent = `${len} / 2000`;

    // Enable/disable send
    sendBtn.disabled = messageInput.value.trim().length === 0;
});

messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (!sendBtn.disabled && !isWaiting) {
            sendMessage();
        }
    }
});

// ============================================
//  CONVERSATIONS MANAGEMENT
// ============================================
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substring(2, 8);
}

function createConversation(firstMessage) {
    const conv = {
        id: generateId(),
        title: firstMessage.substring(0, 40) + (firstMessage.length > 40 ? "..." : ""),
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
    conversations.unshift(conv);
    saveConversations();
    return conv;
}

function saveConversations() {
    localStorage.setItem("nexus_conversations", JSON.stringify(conversations));
    renderConversationsList();
}

function deleteConversation(id, event) {
    event.stopPropagation();
    conversations = conversations.filter(c => c.id !== id);
    saveConversations();

    if (activeConversationId === id) {
        activeConversationId = null;
        chatMessages.innerHTML = "";
        welcomeScreen.style.display = "flex";
        chatTitle.textContent = "New Conversation";
    }
    showToast("Conversation deleted");
}

function loadConversation(id) {
    activeConversationId = id;
    const conv = conversations.find(c => c.id === id);
    if (!conv) return;

    chatTitle.textContent = conv.title;
    welcomeScreen.style.display = "none";
    chatMessages.innerHTML = "";

    conv.messages.forEach(msg => {
        appendMessage(msg.role, msg.content, msg.time, false);
    });

    renderConversationsList();
    scrollToBottom();

    // Close mobile sidebar
    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("active");
}

function renderConversationsList(filter = "") {
    const filtered = filter
        ? conversations.filter(c => c.title.toLowerCase().includes(filter.toLowerCase()))
        : conversations;

    // Group by date
    const today = new Date().toDateString();
    const yesterday = new Date(Date.now() - 86400000).toDateString();

    const groups = { today: [], yesterday: [], older: [] };

    filtered.forEach(conv => {
        const d = new Date(conv.createdAt).toDateString();
        if (d === today) groups.today.push(conv);
        else if (d === yesterday) groups.yesterday.push(conv);
        else groups.older.push(conv);
    });

    let html = "";

    if (groups.today.length) {
        html += '<div class="conv-section-label">Today</div>';
        html += groups.today.map(c => convItemHTML(c)).join("");
    }
    if (groups.yesterday.length) {
        html += '<div class="conv-section-label">Yesterday</div>';
        html += groups.yesterday.map(c => convItemHTML(c)).join("");
    }
    if (groups.older.length) {
        html += '<div class="conv-section-label">Older</div>';
        html += groups.older.map(c => convItemHTML(c)).join("");
    }

    if (!html) {
        html = `<div style="padding: 24px 16px; text-align: center; color: var(--text-muted); font-size: 0.8125rem;">
            No conversations yet
        </div>`;
    }

    conversationsList.innerHTML = html;
}

function convItemHTML(conv) {
    const isActive = conv.id === activeConversationId ? "active" : "";
    const lastMsg = conv.messages.length > 0 ? conv.messages[conv.messages.length - 1].content : "No messages";
    const preview = lastMsg.substring(0, 50) + (lastMsg.length > 50 ? "..." : "");

    return `
        <div class="conv-item ${isActive}" onclick="loadConversation('${conv.id}')">
            <div class="conv-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
            </div>
            <div class="conv-info">
                <div class="conv-title">${escapeHtml(conv.title)}</div>
                <div class="conv-preview">${escapeHtml(preview)}</div>
            </div>
            <button class="conv-delete" onclick="deleteConversation('${conv.id}', event)" title="Delete">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
            </button>
        </div>
    `;
}

searchInput.addEventListener("input", () => {
    renderConversationsList(searchInput.value);
});

// ============================================
//  NEW CHAT
// ============================================
newChatBtn.addEventListener("click", () => {
    activeConversationId = null;
    chatMessages.innerHTML = "";
    welcomeScreen.style.display = "flex";
    chatTitle.textContent = "New Conversation";
    renderConversationsList();

    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("active");
});

// ============================================
//  MESSAGE RENDERING
// ============================================
function getTimeString() {
    return new Date().toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true });
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function formatResponse(text) {
    // Basic markdown-like formatting
    let formatted = escapeHtml(text);

    // Bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Inline code
    formatted = formatted.replace(/`(.*?)`/g, '<code style="background: var(--surface-glass); padding: 2px 6px; border-radius: 4px; font-family: JetBrains Mono, monospace; font-size: 0.85em;">$1</code>');
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

function appendMessage(role, content, time, animate = true) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role}`;
    if (!animate) msgDiv.style.animation = "none";
    if (!animate) msgDiv.style.opacity = "1";

    const isUser = role === "user";
    const displayContent = isUser ? escapeHtml(content) : formatResponse(content);

    msgDiv.innerHTML = `
        <div class="message-avatar">
            ${isUser ? "V" : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
            </svg>`}
        </div>
        <div class="message-content">
            <div class="message-sender">
                ${isUser ? "You" : "NexusAI"}
                <span class="message-time">${time}</span>
            </div>
            <div class="message-bubble">${displayContent}</div>
            ${!isUser ? `
            <div class="message-actions">
                <button class="msg-action-btn" onclick="copyMessage(this)">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                    </svg>
                    Copy
                </button>
            </div>
            ` : ""}
        </div>
    `;

    chatMessages.appendChild(msgDiv);
}

function copyMessage(btn) {
    const bubble = btn.closest(".message-content").querySelector(".message-bubble");
    navigator.clipboard.writeText(bubble.textContent).then(() => {
        showToast("Copied to clipboard");
    });
}

function scrollToBottom() {
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 50);
}

// ============================================
//  SEND MESSAGE
// ============================================
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isWaiting) return;

    isWaiting = true;

    // Hide welcome screen
    welcomeScreen.style.display = "none";

    // Create conversation if needed
    if (!activeConversationId) {
        const conv = createConversation(message);
        activeConversationId = conv.id;
        chatTitle.textContent = conv.title;
    }

    // Add user message
    const time = getTimeString();
    appendMessage("user", message, time);

    // Save to conversation
    const conv = conversations.find(c => c.id === activeConversationId);
    if (conv) {
        conv.messages.push({ role: "user", content: message, time });
        conv.updatedAt = new Date().toISOString();
        saveConversations();
    }

    // Clear input
    messageInput.value = "";
    messageInput.style.height = "auto";
    sendBtn.disabled = true;
    charCount.textContent = "0 / 2000";

    // Show typing
    typingIndicator.classList.remove("typing-hidden");
    scrollToBottom();

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: userId,
                message: message
            })
        });

        const data = await res.json();
        const aiResponse = data.response || "Sorry, I couldn't process that.";
        const aiTime = getTimeString();

        // Hide typing
        typingIndicator.classList.add("typing-hidden");

        // Add AI response
        appendMessage("ai", aiResponse, aiTime);

        // Save AI response
        if (conv) {
            conv.messages.push({ role: "ai", content: aiResponse, time: aiTime });
            conv.updatedAt = new Date().toISOString();
            saveConversations();
        }

    } catch (error) {
        typingIndicator.classList.add("typing-hidden");
        appendMessage("ai", `⚠️ Unable to reach the server. The backend at ${API_URL} might be off or starting up.`, getTimeString());
        console.error("Chat error:", error);
    }

    isWaiting = false;
    scrollToBottom();
    messageInput.focus();
}

// ============================================
//  QUICK PROMPTS
// ============================================
function usePrompt(text) {
    messageInput.value = text;
    messageInput.dispatchEvent(new Event("input"));
    messageInput.focus();
    sendMessage();
}

// ============================================
//  TOAST NOTIFICATIONS
// ============================================
function showToast(message) {
    // Remove existing toast
    const existing = document.querySelector(".toast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add("show");
    });

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// ============================================
//  INIT
// ============================================
renderConversationsList();
messageInput.focus();
