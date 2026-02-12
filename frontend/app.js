const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

// Create WhatsApp client
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "mybot"
    }),
    puppeteer: {
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// Generate QR code for authentication
client.on('qr', (qr) => {
    console.log('\n📱 QR Code received! Scan it with your WhatsApp:');
    qrcode.generate(qr, { small: true });
});

// Client is ready
client.on('ready', () => {
    console.log('\n✅ WhatsApp bot is ready and listening for messages!');
    console.log('Bot is now connected and will respond to messages.\n');
});

// Authentication successful
client.on('authenticated', () => {
    console.log('✅ Authentication successful!');
});

// Authentication failed
client.on('auth_failure', (msg) => {
    console.error('❌ Authentication failed:', msg);
});

// Client disconnected
client.on('disconnected', (reason) => {
    console.log('⚠️ Client was disconnected:', reason);
});

// Listen for incoming messages
client.on('message', async (message) => {
    console.log('\n📨 Message received!');
    console.log('From:', message.from);
    console.log('Body:', message.body);
    console.log('Is Group:', message.from.endsWith('@g.us'));
    console.log('Is from me:', message.fromMe);

    // Skip messages from the bot itself
    if (message.fromMe) {
        console.log('⏭️  Skipping - message from bot itself');
        return;
    }

    // Process messages with content
    if (message.body && message.body.trim() !== '') {
        const query = message.body;
        console.log(`🤖 Processing query: ${query}`);

        try {
            // Call your backend API
            const response = await axios({
                method: 'post',
                url: 'http://localhost:8000/ask_ai',
                responseType: 'stream',
                params: { 'query': query }
            });

            let buffer = "";

            response.data.on('data', (chunk) => {
                buffer += chunk.toString();
            });

            response.data.on('end', async () => {
                try {
                    console.log(`✅ Sending response to ${message.from}`);
                    await message.reply(buffer);
                    console.log('✅ Response sent successfully');
                } catch (error) {
                    console.error('❌ Error sending response:', error);
                    await message.reply("Something failed when trying to retrieve answer: " + error.message);
                }
            });

            response.data.on('error', async (err) => {
                console.error('❌ Stream error:', err);
                await message.reply("Stream error while retrieving the answer: " + err.message);
            });

        } catch (error) {
            console.error('❌ Error calling API:', error);
            await message.reply("Something failed when trying to retrieve answer: " + error.message);
        }
    }
});

// Initialize the client
console.log('🚀 Starting WhatsApp bot...');
client.initialize();
