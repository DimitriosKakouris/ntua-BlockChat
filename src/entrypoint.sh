#!/bin/bash


apt update && apt-get install nano -y 


# Start WebSocket server in the background
python /app/websockets_serve.py --port $PORT --ip $IP &

# Execute CLI script in the foreground
python /app/client.py --port $PORT --ip $IP 
