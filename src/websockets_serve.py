import asyncio
import os
import json
import websockets
from dotenv import load_dotenv
from nodes import Node
from block import genesis

# Assuming the removal of the direct import from the client script for IP and port settings
# Instead, use environment variables or default values
IP_ADDRESS = os.getenv("IP", "127.0.0.1")
PORT = os.getenv("PORT", 8000)

node = Node()

# Load environment variables and set up node details
load_dotenv()
total_nodes = int(os.getenv('TOTAL_NODES', 5))
total_bcc = total_nodes * 1000

bootstrap_node = {
    'ip': os.getenv('BOOTSTRAP_IP', '127.0.0.1'),
    'port': os.getenv('BOOTSTRAP_PORT', '8000')
}

# Debug prints
print('IP address: ', IP_ADDRESS)
print('PORT: ', PORT)

node.ip = IP_ADDRESS
node.port = str(PORT)


# Step 4. 
# See if node is Bootstrap node
if IP_ADDRESS == bootstrap_node["ip"] and str(PORT) == bootstrap_node["port"]:
    node.id = 0
    print("I am bootstrap")

# Step 5.
# Register node to the cluster
async def register_node():
    if node.id == 0:
        # Add himself to ring
        node.register_node_to_ring(node.id, node.ip, node.port, node.wallet.public_key, total_bcc)
        genesis(node.wallet.public_key, total_nodes)

    else:
        await node.unicast_node(bootstrap_node)

def get_balance():
    return node.wallet.get_balance()

def view_last_block_transactions():
    last_block = node.chain.blocks[-1]
    return last_block.view_block()

def new_transaction(receiver_address, amount):
    return node.create_transaction(receiver_address, 'coin', amount, message=None)

def new_message(receiver_address, message):
    return node.create_transaction(receiver_address, 'message', 0, message)

def stake(amount):
    stake_result = node.stake(amount)
    if not stake_result:
        print("Stake failed")

async def handler(websocket, path):
    async for message in websocket:

        data = json.loads(message)
        
        action = data.get('action')
        
        
        if action == 'register_node':
            node_key = data['public_key']
            node_ip = data['ip']
            node_port = data['port']
            node_id = len(node.ring)
            print (node.id)
            
            await register_node()
            
            if node_id == 5 - 1:
                print("All nodes have joined the network")
                for ring_node in node.ring:
                    if ring_node["id"] != node.id:
                        await node.share_chain(ring_node)
                        await node.share_ring(ring_node)
                for ring_node in node.ring:
                    if ring_node["id"] != node.id:
                        node.create_transaction(ring_node['public_key'], ring_node['id'], 1000)
            
            await websocket.send(json.dumps({'id': node_id}))

        elif action == 'new_transaction':
            # Extract relevant data
            receiver = data['data']['receiver']
            amount = data['data']['amount']
            # Perform the transaction
            response = node.new_transaction(receiver, amount)
            # Send back a JSON response
            await websocket.send(json.dumps({'response': response}))
        
        elif data['action'] == 'validate_transaction':
            new_transaction = data['transaction']
            if node.validate_transaction(new_transaction):
                await websocket.send(json.dumps({'message': "OK"}))
            else:
                await websocket.send(json.dumps({'message': "The signature is not valid"}))

        elif data['action'] == 'get_balance':
            balance = get_balance()
            await websocket.send(json.dumps({'balance': balance}))

# Start the WebSocket server
async def main():
    async with websockets.serve(handler, IP_ADDRESS, PORT):
        print(f"Server started at ws://{IP_ADDRESS}:{PORT}")
        print(node.id)
        await asyncio.Future()  # This will keep the server running indefinitely

# Run the server
if __name__ == "__main__":
    asyncio.run(main())

                


