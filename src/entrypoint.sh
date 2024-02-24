#!/bin/bash


# apt update && apt-get install nano -y 


# Start WebSocket server in the background
python /app/websockets_serve.py  &

# Execute CLI script in the foreground
python /app/client.py  

# cd /app/frontend/blockchat_client npm build .


# cd /app/frontend/blockchat_client npm start