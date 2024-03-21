#!/bin/bash

# Start WebSocket server in the background
python /app/wserve.py  &

# Execute CLI script in the foreground
python /app/client.py  

# cd /app/frontend/blockchat_client npm build .


# cd /app/frontend/blockchat_client npm start