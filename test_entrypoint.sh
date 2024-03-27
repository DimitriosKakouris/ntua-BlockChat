#!/bin/bash

if [ $# -eq 2 ]; then
  export TOTAL_NODES="$1"
  export BLOCK_CAPACITY="$2"
  export COMPUTE_JUSTICE="False"
elif [ $# -eq 3 ]; then
  export TOTAL_NODES="$1"
  export BLOCK_CAPACITY="$2"
  if [[ "$3" == "True" || "$3" == "False" ]]; then
    export COMPUTE_JUSTICE="$3"
  else
    echo "COMPUTE_JUSTICE must be 'True' or 'False'."
    exit 1
  fi
else
  echo "Usage: $0 TOTAL_NODES BLOCK_CAPACITY [COMPUTE_JUSTICE]"
  echo "COMPUTE_JUSTICE is optional and must be 'True' or 'False'."
  exit 1
fi
# Start WebSocket server in the background
python ./src/wserve.py 
