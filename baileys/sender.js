const express = require("express");

function startSender(sock) {
    const app = express();
    app.use(express.json());

    // Python agent calls this endpoint to send a message back to WhatsApp
    app.post("/send", async (req, res) => {
        const { text } = req.body;

        if (!text) {
            return res.status(400).json({ error: "missing text" });
        }

        try {
            // Try phone JID first, fall back to LID if that fails
            // Normalize: strip device suffix e.g. ":30"
            const phoneJid = sock.user.id.replace(/:\d+@/, "@");
            const lidJid   = sock.user.lid ? sock.user.lid.replace(/:\d+@/, "@") : null;

            // Use phone JID first (more reliable), fall back to LID
            const targetJid = phoneJid || lidJid;

            await sock.sendMessage(targetJid, { text });
            res.json({ ok: true });
        } catch (err) {
            console.error("❌ Send error:", err.message);
            res.status(500).json({ error: err.message });
        }
    });

    app.listen(8766, "127.0.0.1", () => {
        console.log("📡 Sender running on :8766");
    });
}

module.exports = startSender;