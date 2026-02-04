const net = require('net');

// Get server name from command line or use localhost
const serverName = process.argv[2] || 'localhost';
const serverPort = 12000;

function generateRandomMessage(length) {
    const chars = 'abcdefghijklmnopqrstuvwxyz ';
    let message = '';
    for (let i = 0; i < length; i++) {
        message += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return message;
}

// Generate random number of messages (1-10)
const numMessages = Math.floor(Math.random() * 10) + 1;
console.log(`Client will send ${numMessages} random messages to ${serverName}:${serverPort}`);

let messagesSent = 0;

function sendMessage(messageNum) {
    const client = new net.Socket();

    client.connect(serverPort, serverName, () => {
        // Generate and send random message
        const messageLength = Math.floor(Math.random() * 21) + 10; // 10-30 characters
        const message = generateRandomMessage(messageLength);

        console.log(`\n[Message ${messageNum}/${numMessages}] Sending: ${message}`);
        client.write(message);
    });

    client.on('data', (data) => {
        console.log(`[Message ${messageNum}/${numMessages}] From Server: ${data.toString()}`);
        client.destroy();

        messagesSent++;

        // Send next message or finish
        if (messagesSent < numMessages) {
            sendMessage(messagesSent + 1);
        } else {
            console.log(`\n✓ Successfully sent all ${numMessages} messages. Client terminating.`);
        }
    });

    client.on('error', (err) => {
        console.error('ERROR:', err.message);
        console.error(`Make sure the server is running at ${serverName}:${serverPort}`);
        process.exit(1);
    });
}

// Start sending messages
sendMessage(1);
