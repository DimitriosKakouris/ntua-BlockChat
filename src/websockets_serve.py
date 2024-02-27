import asyncio
import os
import json
import websockets
from dotenv import load_dotenv
from nodes import Node
from block import Block
from transaction import Transaction


# Assuming the removal of the direct import from the client script for IP and port settings
# Instead, use environment variables or default values
IP_ADDRESS = os.getenv("IP", "172.18.0.2")
PORT = os.getenv("PORT", 8000)

# global node
# global bootstrap_node

node = Node()

# Load environment variables and set up node details
load_dotenv()
total_nodes = int(os.getenv('TOTAL_NODES', 3))
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

        print("Registered Bootstrap node to ring")
        transaction = Transaction(
            sender_address='0',
            receiver_address=node.wallet.public_key,
            type_of_transaction='coin',
            amount=total_bcc,
            nonce=1,
            message=None
        )
        
        node.transaction_pool.append(transaction)
        node.wallet.balance += total_bcc

        print("Genesis transaction added to transaction pool")
        genesis_block = Block(1,'1')
      
        genesis_block.validator = 0
        genesis_block.transactions.append(transaction)

        node.chain.add_block(genesis_block)

        


        print("Genesis block added to chain")



    else: 
        await node.unicast_node(bootstrap_node)
  


def get_balance():
    return node.wallet.get_balance()

def view_last_block_transactions():
    last_block = node.chain.blocks[-1]
    return last_block.view_block()


def new_message(receiver_address, message):
    return node.create_transaction(receiver_address, 'message', 0, message)

def stake(amount):
    node.stake = amount
    return node.stake
  


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

async def handler(websocket):
    global connected_nodes
  

    async for message in websocket:
        data = json.loads(message)
        

        if data['action'] == 'register_node':
            # Create a Condition
            node_joined_condition = asyncio.Condition()

            # In the 'register_node' action handler
            async with node_joined_condition:
                new_node_data = data.get('data')
                connected_nodes.append(new_node_data)

                # If 4 nodes have joined, notify all tasks waiting on the Condition
                if len(connected_nodes) >= 2:
                    node_joined_condition.notify_all()

            # In the part of your code that needs to wait for 4 nodes to join
            async with node_joined_condition:
                while len(connected_nodes) < 2:
                    await node_joined_condition.wait()


            print(f"{len(connected_nodes)} nodes have joined the network")

            # Register the nodes to the ring
            for i, node_data in enumerate(connected_nodes):
                bootstrap_node.register_node_to_ring(i+1, node_data['ip'], node_data['port'], node_data['public_key'])
                

            print("Ring:", bootstrap_node.ring)
            # Share the chain and the ring
            for ring_node in bootstrap_node.ring:
                if ring_node['id'] != 0:
                    print("ring_node:", ring_node['id'])
                    await bootstrap_node.share_chain(ring_node)
                    # In the share_ring method
                    print(f"Sharing ring with node {ring_node['id']}")
                    await bootstrap_node.share_ring(ring_node)
                  

            for ring_node in bootstrap_node.ring:
                if ring_node['id'] != 0:
                    print("Sending coins to node", ring_node['id'])

                    await bootstrap_node.create_transaction(ring_node['public_key'],'coin' ,1000)
                   

            # Reset the connected nodes
            connected_nodes = []
            await websocket.send(json.dumps({'status' :'Entered the network','id': node.id}))
           

        elif data['action'] == 'new_transaction':
           
            receiver = data['data']['receiver']
            for ring_node in node.ring:
                if ring_node['id'] == int(receiver):
                    receiver = ring_node['public_key']
                    break

            amount = data['data']['amount']
            print(f"New transaction in websockets server: {receiver} -> {amount}")
            # Perform the transaction
            response = await node.create_transaction(receiver, 'coin', amount)
            print(response)
            # Send back a JSON response
            await websocket.send(json.dumps({'response': response}))

     
        elif data['action'] == 'new_message':
           
            receiver = data['data']['receiver']
            for ring_node in node.ring:
                if ring_node['id'] == int(receiver):
                    receiver = ring_node['public_key']
                    break

            
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
            node_id = node.id

            await websocket.send(json.dumps({'Node ID':node_id,'chain':node.chain.to_dict(),'wallet_address':wallet_address,'balance': balance}))


        elif data['action'] == 'update_balance':
            for trans in node.transaction_pool:
                # print(f'trans: {trans}')
                # print(f'from node.chain.blocks[-1] the first {node.chain.blocks[-1].transactions}')
                # print(f'Nodes chain{node.chain.to_dict()}')
                if any(trans.transaction_id == transaction.transaction_id for transaction in node.chain.blocks[-1].transactions):
                    print("Found transaction in block")
                    if trans.sender_address == node.wallet.public_key:
                        node.wallet.balance -= trans.to_dict()['amount']
                    
                    if trans.receiver_address == node.wallet.public_key:
                        node.wallet.balance += trans.to_dict()['amount']

                    node.transaction_pool.remove(trans)
        
            print(f"Node {node.id} received 'update_balance' action")

            await websocket.send(json.dumps({'message': "Balance updated"}))



        elif data['action'] == 'update_ring':
            new_ring = data['data']
            node.ring = new_ring

            for ring_node in node.ring:
                if ring_node['ip']==node.ip and ring_node['port']==node.port:
                    node.id = ring_node['id']
                    break   
            print(f"Node {node.id} received 'update_ring' action")

            await websocket.send(json.dumps({'message': "Ring updated"}))

        elif data['action'] == 'update_chain':
           
            # Get the serialized chain from the other node
            serialized_chain = data['data']
            # Deserialize the chain
            chain = node.chain.from_dict(serialized_chain)
            node.chain = chain

            await websocket.send(json.dumps({'message': "Chain updated"}))

        elif data['action'] == 'stake':
            amount = data['data']['amount']
            node.stake(amount)

            await websocket.send(json.dumps({'message': f"Stake updated to: {node.stake}"}))

        elif data['action'] == 'get_stake':
            await websocket.send(json.dumps({'stake': node.stake}))

        elif data['action'] == 'selected_as_validator':
            minting_time = await node.chain.mint_block(node)
            await websocket.send(json.dumps({'minting_time': minting_time}))

     
        
        elif data['action'] == 'update_block':
            transaction = data['data']
            
            if transaction['recipient_address'] == node.wallet.public_key:
                transaction_recv = Transaction.from_dict(transaction)
                node.transaction_pool.append(transaction_recv)

            elif transaction['sender_address'] == node.wallet.public_key:
                transaction_send = Transaction.from_dict(transaction)
                node.transaction_pool.append(transaction_send)

            transaction = Transaction.from_dict(transaction)
            res = await node.add_transaction_to_block(transaction)

            if res !=  0:
                await websocket.send(json.dumps({'message':'Minting was done','minting_time': res}))
            else:
                await websocket.send(json.dumps({'message':'Block is not full yet'}))

        elif data['action'] == 'new_block':
            if node.chain.blocks[-1].current_hash != data['data']['hash']:
                node.chain.add_block(Block.from_dict(data['data']))
            node.current_block = None   

            await websocket.send(json.dumps({'status':200,'message':'Block added to chain'}))



# Start the WebSocket server
async def main():
    async with websockets.serve(handler, IP_ADDRESS, PORT):
        print(f"Server started at ws://{IP_ADDRESS}:{PORT}")
        
        await register_node()  # Register the node with the bootstrap node
        await asyncio.Future()  # This will keep the server running indefinitely

# Run the server
if __name__ == "__main__":
    asyncio.run(main())

                


