const axios = require("axios");

async function startListener(sock) {
    sock.ev.on("messages.upsert", async (m) => {
        if (m.type !== "notify") return;

        const msg = m.messages[0];
        if (!msg.message) return;

        // Only process messages sent by yourself
        if (!msg.key.fromMe) return;

        // Normalize a JID: strip device suffix "917483218396:30@s.whatsapp.net" → "917483218396@s.whatsapp.net"
        const normalizeJid = (jid = "") => jid.replace(/:\d+@/, "@");

        const remoteJid = normalizeJid(msg.key.remoteJid || "");

        // Build both forms of our own JID — phone number JID and LID
        const myPhoneJid = normalizeJid(sock.user?.id || "");
        const myLidJid   = normalizeJid(sock.user?.lid || "");

        // Saved Messages = remoteJid matches either our phone JID or our LID
        const isSavedMessages =
            (myPhoneJid && remoteJid === myPhoneJid) ||
            (myLidJid   && remoteJid === myLidJid);

        if (!isSavedMessages) return;

        // Extract text — handle all common message types
        const text =
            msg.message.conversation ||
            msg.message.extendedTextMessage?.text ||
            msg.message.imageMessage?.caption ||
            msg.message.videoMessage?.caption ||
            "";

        if (!text.trim()) return;

        // Only respond to messages starting with "/"
        if (!text.trim().startsWith("/")) return;

        console.log("📩 Received:", text);

        try {
            await axios.post("http://127.0.0.1:8765/message", {
                text: text.trim().slice(1).trim(), // strip leading "/"
                msg_id: msg.key.id,
                sender: myPhoneJid || myLidJid     // stable session identifier
            });
        } catch (err) {
            console.error("❌ Failed to POST to agent:", err.message);
        }
    });
}

module.exports = startListener;