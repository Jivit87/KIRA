const axios = require("axios");

async function startListener(sock) {
    sock.ev.on("messages.upsert", async ({ messages }) => {
        const msg = messages[0];
        if (!msg.message) return;

        // Only process your own messages
        if (!msg.key.fromMe) return;

        const text = msg.message.conversation || msg.message.extendedTextMessage?.text;

        if (!text || !text.startsWith("/")) return;

        // Strip the '/' command prefix before sending to the agent
        const cleanText = text.slice(1).trim();

        const sender = msg.key.remoteJid;

        console.log("📩 Incoming command:", cleanText);

        try {
            // Send to Python agent
            const res = await axios.post("http://127.0.0.1:8765/message", {
                text: cleanText,
                sender
            });

            const reply = res.data.reply;

            // Send reply back to WhatsApp
            await sock.sendMessage(sender, { text: reply });

        } catch (err) {
            console.error("❌ Error:", err.message);

            await sock.sendMessage(sender, {
                text: "⚠️ Something went wrong"
            });
        }
    });
}

module.exports = startListener;