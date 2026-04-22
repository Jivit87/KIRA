const axios = require("axios");

async function startListener(sock) {
    sock.ev.on("messages.upsert", async (m) => {
        if (m.type !== "notify") return;
        
        const msg = m.messages[0];
        if (!msg.message) return;

        // Only process messages from yourself (Saved Messages)
        const isFromMe = msg.key.fromMe;
        const isSavedMessages = msg.key.remoteJid === (sock.user?.id.replace(':0@', '@s.whatsapp.net') || '');
        
        if (!isFromMe || !isSavedMessages) return;

        // Extract text from message
        const text = msg.message.conversation || msg.message.extendedTextMessage?.text;
        if (!text || !text.trim()) return;

        console.log("📩 Received:", text);

        try {
            // Send to Python agent
            await axios.post("http://127.0.0.1:8765/message", {
                text: text,
                msg_id: msg.key.id
            });

        } catch (err) {
            console.error("❌ Failed to POST to agent:", err.message);
        }
    });
}

module.exports = startListener;