const net = require('net');
const readline = require('readline');

// Get server name from command line or use localhost
const serverName = process.argv[2] || 'localhost';
const serverPort = 12000;

console.log(`Connecting to server at ${serverName}:${serverPort}`);

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function sendMessage() {
    rl.question('Input lowercase sentence: ', (sentence) => {
        const client = new net.Socket();

        client.connect(serverPort, serverName, () => {
            console.log('Connected to server');
            client.write(sentence);
        });

        client.on('data', (data) => {
            console.log('From Server:', data.toString());
            client.destroy();

            rl.question('Other message: (Y/N) ', (answer) => {
                if (answer.toUpperCase() === 'N') {
                    console.log('Closing connection...');
                    rl.close();
                } else {
                    sendMessage();
                }
            });
        });

        client.on('error', (err) => {
            console.error('ERROR:', err.message);
            console.error(`Make sure the server is running at ${serverName}:${serverPort}`);
            rl.close();
        });

        client.on('close', () => {
            // Connection closed
        });
    });
}

// Start the client
sendMessage();
