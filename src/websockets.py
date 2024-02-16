import asyncio
import os
import pickle
import argparse
import websockets
from node import Node
# from main import num_nodes
from dotenv import load_dotenv
from block import genesis, Block


################## ARGUMENTS #####################
argParser = argparse.ArgumentParser()
argParser.add_argument( "--port", help="Port in which node is running", default=6789, type=int)
argParser.add_argument("--ip", help="IP of the host")
args = argParser.parse_args()

node = Node()



# Step 2.
# Get info about the cluster, bootstrap node
load_dotenv()
total_nodes = int(os.getenv('TOTAL_NODES'))
total_bcc = total_nodes * 1000

bootstrap_node = {
    'ip': os.getenv('BOOTSTRAP_IP'),
    'port': os.getenv('BOOTSTRAP_PORT')
}

# Step 3.
# Set the IP and PORT
# DOCKER SPECIFIC
ip_address = args.ip
# IP ADDRESS
# if (ip_address is None):
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect(("8.8.8.8", 80))
#     ip_address = s.getsockname()[0]
#     s.close()
print('IP address: ', ip_address) # debug
# PORT
port = args.port
print('PORT: ', port) # debug
node.ip = ip_address
node.port = str(port)

# Step 4. 
# See if node is Bootstrap node
if ip_address == bootstrap_node["ip"] and str(port) == bootstrap_node["port"]:
    node.id = 0
    print("I am bootstrap")

# Step 5.
# Register node to the cluster
if node.id == 0:
    # Add himself to ring
    node.register_node_to_ring(node.id, node.ip, node.port, node.wallet.address, total_bcc)
    genesis(node.wallet.public_key, total_nodes)

else:
    node.unicast_node(bootstrap_node)
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
                        await node.share_chain(ring_node)
                        await node.share_ring(ring_node)
                for ring_node in node.ring:
                    if ring_node["id"] != node.id:
                        node.create_transaction(ring_node['public_key'], ring_node['id'], 1000)
            
            await websocket.send(pickle.dumps({'id': node_id}))

        elif data['action'] == 'validate_transaction':
            new_transaction = data['transaction']
            if node.validate_transaction(new_transaction):
                await websocket.send(pickle.dumps({'message': "OK"}))
            else:
                await websocket.send(pickle.dumps({'message': "The signature is not valid"}))

        elif data['action'] == 'get_balance':
            balance = await get_balance()
            await websocket.send(pickle.dumps({'balance': balance}))

        # Add other actions here, e.g., 'receive_transaction', 'receive_block', etc.
        # You need to define the structure of your messages to include an 'action' field
        # and the necessary data for each action.
                
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




# port = os.getenv('PORT', 'port-number')
# Start the WebSocket server
start_server = websockets.serve(handler, ip_address, 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
