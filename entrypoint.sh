#!/bin/bash

# Start WebSocket server in the background
python ./src/wserve.py  &

# Execute CLI script in the foreground
python ./src/client.py  

# cd /app/frontend/blockchat_client npm build .


# cd /app/frontend/blockchat_client npm start