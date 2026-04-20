const { default: makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion, DisconnectReason } = require("@whiskeysockets/baileys");
const { Boom } = require("@hapi/boom");
const qrcode = require("qrcode-terminal");

const startListener = require("./listener");
const startSender = require("./sender");

async function startWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState("./auth");
    const { version, isLatest } = await fetchLatestBaileysVersion();

    const sock = makeWASocket({
        version,
        auth: state,
    });

    sock.ev.on("connection.update", (update) => {
        const { connection, qr } = update;

        if (qr) {
            qrcode.generate(qr, { small: true });
        }

        if (connection === "open") {
            console.log("✅ WhatsApp connected");
        }

        if (connection === "close") {
            const shouldReconnect = update.lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log("⚠️ Connection closed, reconnecting:", shouldReconnect);
            if (shouldReconnect) {
                startWhatsApp();
            }
        }
    });

    sock.ev.on("creds.update", saveCreds);

    // Attach modules
    startListener(sock);
    startSender(sock);
}

startWhatsApp();