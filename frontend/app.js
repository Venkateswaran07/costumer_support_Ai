const userId = "user1";

async function sendMessage() {
    const input = document.getElementById("input");
    const message = input.value;

    if (!message) return;

    addMessage("You: " + message);

    const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_id: userId,
            message: message
        })
    });

    const data = await res.json();

    addMessage("AI: " + data.response);

    input.value = "";
}

function addMessage(msg) {
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<p>${msg}</p>`;
}
