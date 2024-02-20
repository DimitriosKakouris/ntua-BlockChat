#!/bin/bash

# Define the network name
network="ntua-blockchain_blockchat"

# Define the Docker image name
image="ntua-blockchain"

# Commands to run each container in a new GNOME terminal window
gnome-terminal -- bash -c "sudo docker run -it -e PORT=8000 -e IP=172.18.0.2 -p 8000:8000 --network $network --rm $image; exec bash"
gnome-terminal -- bash -c "sudo docker run -it -e PORT=8001 -e IP=172.18.0.3 -p 8001:8000 --network $network --rm $image; exec bash"
gnome-terminal -- bash -c "sudo docker run -it -e PORT=8002 -e IP=172.18.0.4 -p 8002:8000 --network $network --rm $image; exec bash"
gnome-terminal -- bash -c "sudo docker run -it -e PORT=8003 -e IP=172.18.0.5 -p 8003:8000 --network $network --rm $image; exec bash"
gnome-terminal -- bash -c "sudo docker run -it -e PORT=8004 -e IP=172.18.0.6 -p 8004:8000 --network $network --rm $image; exec bash"


