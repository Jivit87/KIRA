const express = require("express");

function startSender(sock) {
    const app = express();
    app.use(express.json());

    app.post("/send", async (req, res) => {
        const { text, to } = req.body;

        try {
            await sock.sendMessage(to, { text });
            res.sendStatus(200);
        } catch (err) {
            console.error(err);
            res.sendStatus(500);
        }
    });

    app.listen(8766, () => {
        console.log("📡 Sender running on 8766");
    });
}

module.exports = startSender;