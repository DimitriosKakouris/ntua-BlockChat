#!/bin/bash
export TEST_MODE="False"
export COMPUTE_JUSTICE="False"

if [ $# -eq 2 ]; then
  export TOTAL_NODES="$1"
  export BLOCK_CAPACITY="$2"
else
  echo "Usage: $0 TOTAL_NODES BLOCK_CAPACITY"
  exit 1
fi

# Start WebSocket server in the background
python /app/wserve.py  &
WSERVE_PID=$!

# Execute CLI script in the foreground
python /app/client.py 

# After the client script finishes, kill the WebSocket server
kill $WSERVE_PID