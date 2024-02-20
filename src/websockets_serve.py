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
    'ip': os.getenv('BOOTSTRAP_IP', '172.18.0.2'),
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
    bootstrap_node = node
    print("I am bootstrap")

# Step 5.
# Register node to the cluster
async def register_node():
    if node.id == 0:
        # Add himself to ring
        node.register_node_to_ring(node.id, node.ip, node.port, node.wallet.public_key)
        node.chain.add_block(genesis(node.wallet.public_key, total_nodes))

    else: 
        print("Just before unicasting to the bootstrap node")
        ws_url = f"ws://{bootstrap_node['ip']}:{bootstrap_node['port']}"
        node_info = {
                    'action': 'register_node',
                    'data': {
                        'ip': node.ip,
                        'port': node.port,
                        'public_key': node.wallet.public_key
                    }
                }
        print("I have unicasted to the bootstrap node")

        async with websockets.connect(ws_url) as websocket:
            # Send the registration information as a JSON string
            await websocket.send(json.dumps(node_info))
            
            # Wait for a response from the bootstrap node
            response = await websocket.recv()
            response_data = json.loads(response)
            
            node.id = response_data['id']
            print('My ID is:', node.id)

        # await node.share_ring(bootstrap_node)
            


def get_balance():
    return node.wallet.get_balance()

def view_last_block_transactions():
    last_block = node.chain.blocks[-1]
    return last_block.view_block()

# async def new_transaction(receiver_address, amount):
#     return await node.create_transaction(receiver_address, 'coin', amount, message=None)

def new_message(receiver_address, message):
    return node.create_transaction(receiver_address, 'message', 0, message)

def stake(amount):
    stake_result = node.stake(amount)
    if not stake_result:
        print("Stake failed")


async def send_websocket_request(action, data,ip, port):
    # Define the WebSocket URL
    ws_url = f"ws://{ip}:{port}"

    # Define the request
    request = {
        'action': action,
        'data': data
    }

    print(f"Sending request to {ws_url}: {request}")
    # Connect to the WebSocket server and send the request
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(json.dumps(request))

        # Wait for a response from the server
        response = await websocket.recv()

    # Return the response
    return json.loads(response)

connected_nodes = []

async def handler(websocket, path):
    global connected_nodes

    async for message in websocket:
        data = json.loads(message)
        

        if data['action'] == 'register_node':
            new_node_data = data.get('data')

            # Store the new node's data
            connected_nodes.append(new_node_data)

            # If there are 4 nodes connected, broadcast the chain and the ring
            if len(connected_nodes) == 1:
                print("1 nodes have joined the network")

                # Register the nodes to the ring
                for i, node_data in enumerate(connected_nodes):
                    bootstrap_node.register_node_to_ring(i+1, node_data['ip'], node_data['port'], node_data['public_key'])

                print("Ring:", bootstrap_node.ring)
                # Share the chain and the ring
                for ring_node in bootstrap_node.ring:
                    if ring_node["id"] != 0:
                        await bootstrap_node.share_chain(ring_node)
                        await bootstrap_node.share_ring(ring_node)
                        print("Sending coins to node", ring_node['id'])
                        await node.create_transaction(ring_node['public_key'],'coin' ,1000)

                # Reset the connected nodes
                connected_nodes = []

            # Send back the node ID
            node_id = len(bootstrap_node.ring) - 1
            await websocket.send(json.dumps({'id': node_id}))


        elif data['action'] == 'new_transaction':
            # Extract relevant data
            receiver = data['data']['receiver']
            amount = data['data']['amount']
            print(f"New transaction in websockets server: {receiver} -> {amount}")
            # Perform the transaction
            response = await node.create_transaction(receiver, 'coin', amount)
            print(response)
            # Send back a JSON response
            await websocket.send(json.dumps({'response': response}))

        elif data['action'] == 'new_message':
            # Extract relevant data
            receiver = data['data']['receiver']
            message = data['data']['message']

            # Perform the transaction
            response = await node.create_transaction(receiver, 'message', 0, message)

            # Send back a JSON response
            await websocket.send(json.dumps({'response': response}))
        
        elif data['action'] == 'validate_transaction':
            new_transaction = data['transaction']
            if node.validate_transaction(new_transaction):
                await websocket.send(json.dumps({'message': "OK"}))
            else:
                await websocket.send(json.dumps({'message': "The signature is not valid"}))

        elif data['action'] == 'get_balance':
            print("Getting balance")
            balance = get_balance()
            wallet_address = node.wallet.public_key
            await websocket.send(json.dumps({'wallet_address':wallet_address,'balance': balance}))

        elif data['action'] == 'update_ring':
            new_ring = data['data']
            print("Updating ring")
            node.ring = new_ring
            print("Ring updated")

            await websocket.send(json.dumps({'message': "Ring updated"}))

        elif data['action'] == 'update_chain':
           
            # Get the serialized chain from the other node
            serialized_chain = data['data']

            # Deserialize the chain
            chain = node.chain.from_dict(serialized_chain)

            # print("Chain:", chain)
            # print("Blocks:", chain.blocks)
            # print("Number of blocks:", chain.size())
            # print("Before iteration")
            # Add the chain to the node's blockchain
            node.chain = chain
            # for block in chain.blocks:
            #     try:
            #         node.chain.add_block(block)
            #     except Exception as e:
            #         print("Exception during block addition:", e)
            # print("After iteration")
                    
            
            await websocket.send(json.dumps({'message': "Chain updated"}))

        elif data['action'] == 'update_transaction_pool':
            new_transaction = data['data']
            node.transaction_pool.append(new_transaction)
            await websocket.send(json.dumps({'status':'OK','message': "Transaction pool updated"}))
            
# Start the WebSocket server
async def main():
    async with websockets.serve(handler, IP_ADDRESS, PORT):
        print(f"Server started at ws://{IP_ADDRESS}:{PORT}")
        # Register the node with the bootstrap node
        await register_node()
        await asyncio.Future()  # This will keep the server running indefinitely

# Run the server
if __name__ == "__main__":
    asyncio.run(main())

                


