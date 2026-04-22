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
            // Send to Saved Messages (your own number)
            const jid = sock.user.id.replace(':0@', '@s.whatsapp.net');
            await sock.sendMessage(jid, { text });
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