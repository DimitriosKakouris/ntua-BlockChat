import asyncio
import os
import pickle
import websockets
from node import Node

node = Node()
num_nodes = 0 #TODO: define it in main.py

# WebSocket server implementation
async def handler(websocket, path):
    async for message in websocket:
        # Determine the type of message received
        # This assumes you're sending some kind of identifiable action in your message
        data = pickle.loads(message)
        
        if data['action'] == 'register_node':
            node_key = data['public_key']
            node_ip = data['ip']
            node_port = data['port']
            node_id = len(node.ring)
            
            node.register_node_to_ring(id=node_id, ip=node_ip, port=node_port, public_key=node_key, balance=0)
            
            if node_id == num_nodes - 1:
                for ring_node in node.ring:
                    if ring_node["id"] != node.id:
                        await share_chain(ring_node)
                        await share_ring(ring_node)
                for ring_node in node.ring:
                    if ring_node["id"] != node.id:
                        node.create_transaction(ring_node['public_key'], ring_node['id'], 100)
            
            await websocket.send(pickle.dumps({'id': node_id}))

        elif data['action'] == 'validate_transaction':
            new_transaction = data['transaction']
            if node.validate_transaction(new_transaction):
                await websocket.send(pickle.dumps({'message': "OK"}))
            else:
                await websocket.send(pickle.dumps({'message': "The signature is not valid"}))

        # Add other actions here, e.g., 'receive_transaction', 'receive_block', etc.
        # You need to define the structure of your messages to include an 'action' field
        # and the necessary data for each action.

# Function placeholders for sharing the chain and ring, adapt as necessary.
async def share_chain(ring_node):
    # Implement sharing the chain with a node
    pass

async def share_ring(ring_node):
    # Implement sharing the ring with a node
    pass

port = os.getenv('PORT', 'port-number')
# Start the WebSocket server
start_server = websockets.serve(handler, "localhost", port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
