import asyncio
import os
import json
import websockets
from dotenv import load_dotenv
from nodes import Node
from block import Block
from transaction import Transaction
from wsmanager import send_websocket_request



node = Node()

# Load environment variables and set up node details
load_dotenv()
IP_ADDRESS = os.getenv("IP", "172.18.0.2")
PORT = os.getenv("PORT", 8000)
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



# See if node is Bootstrap node
if IP_ADDRESS == bootstrap_node["ip"] and str(PORT) == bootstrap_node["port"]:
    node.id = 0
    bootstrap_node = node
    print("I am bootstrap")


# Register node to the cluster
async def register_node():
    if node.id == 0:
        # Add himself to ring
        node.register_node_to_ring(node.id, node.ip, node.port, node.wallet.public_key)

        # print("Registered Bootstrap node to ring")  # print("Registered Bootstrap node to ring")
        transaction = Transaction(
            sender_address='0',
            receiver_address=node.wallet.public_key,
            type_of_transaction='coin',
            amount=total_bcc,
            nonce=1,
            message=None
        )
        
        # node.transaction_pool.append(transaction)
        node.wallet.balance += total_bcc

        # print("Genesis transaction added to transaction pool")
        genesis_block = Block(1,'1')
      
        genesis_block.validator = 0
        genesis_block.transactions.append(transaction)
        node.chain.add_block(genesis_block)
        # print("Genesis block added to chain")



    else: 
        await node.unicast_node(bootstrap_node)
        await send_websocket_request('init_account_space', {}, node.ip, node.port)
        
  


def get_balance():
    return node.wallet.get_balance()

# def view_last_block_transactions():
#     last_block = node.chain.blocks[-1]
#     return last_block.view_block()


# def new_message(receiver_address, message):
#     return node.create_transaction(receiver_address, 'message', 0, message)

# def stake(amount):
#     node.stake = amount
#     return node.stake
  

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


            # print(f"{len(connected_nodes)} nodes have joined the network")

            # Register the nodes to the ring
            for i, node_data in enumerate(connected_nodes):
                bootstrap_node.register_node_to_ring(i+1, node_data['ip'], node_data['port'], node_data['public_key'])
                

            # print("Ring:", bootstrap_node.ring)
            # Share the chain and the ring
            for ring_node in bootstrap_node.ring:
                if ring_node['id'] != 0:
                    # print("ring_node:", ring_node['id'])
                    await bootstrap_node.share_chain(ring_node)
                    # In the share_ring method
                    # print(f"Sharing ring with node {ring_node['id']}")
                    await bootstrap_node.share_ring(ring_node)
                    await bootstrap_node.share_account_space(ring_node)
                    # await send_websocket_request('init_account_space', {}, ring_node['ip'], ring_node['port'])
                  

            for ring_node in bootstrap_node.ring:
                if ring_node['id'] != 0:
                    # print("Sending coins to node", ring_node['id'])

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
            # print(f"New transaction in websockets server: {receiver} -> {amount}")
            # Perform the transaction
            response = await node.create_transaction(receiver, 'coin', amount)
            # print(response)
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
                await websocket.send(json.dumps({'message': "The signature is not valid or not enough balance"}))

        elif data['action'] == 'get_balance':
            print("Getting balance")
            balance = get_balance()
            wallet_address = node.wallet.public_key
            node_id = node.id

            await websocket.send(json.dumps({'Node ID':node_id,'chain':node.chain.to_dict(),'wallet_address':wallet_address,'balance': balance, 'stake':node.stake_amount}))

        elif data['action'] == 'view_last_transactions':

            # last_block_transactions = node.chain.blocks[-1].transactions
            # last_block_validator = node.chain.blocks[-1].validator
            # last_transactions = [trans.to_dict() for trans in last_block_transactions]
            last_validated_block = node.chain.blocks[-1].view_block()
            await websocket.send(json.dumps(last_validated_block))
            # await websocket.send(json.dumps({'Last validated block info': last_validated_block}))

        elif data['action'] == 'update_balance':
             # Create a copy of the transaction_pool for iteration
            transaction_pool_copy = node.transaction_pool.copy()
            fees_sum = 0
            for trans in transaction_pool_copy:
                if any(trans.transaction_id == transaction.transaction_id for transaction in node.chain.blocks[-1].transactions):
                    flag = 1 if trans.type_of_transaction == 'coin' and (node.id != 0 or trans.nonce != 0) else 0 #bootstrap node isn't charged a fee when executing the genesis transactions
                    if trans.sender_address == node.wallet.public_key and trans.receiver_address != '0': #regural transaction
                        node.wallet.balance -= int(trans.to_dict()['amount']) * (1 + flag * 0.03)
                        fees_sum += flag * 0.03 * int(trans.to_dict()['amount'])
                    
                    elif trans.sender_address == node.wallet.public_key and trans.receiver_address == '0': #transaction is stake(amount)
                        node.wallet.balance += node.stake_amount
                        node.stake_amount = int(trans.to_dict()['amount'])
                        node.wallet.balance -= node.stake_amount

                    if trans.receiver_address == node.wallet.public_key:
                        if trans.type_of_transaction == 'message': #message 
                            fees_sum += int(trans.to_dict()['amount'])
                        else: #regular transaction
                            node.wallet.balance += int(trans.to_dict()['amount'])
                        
                    # Remove the transaction from the original transaction_pool
                    node.transaction_pool.remove(trans)


            for trans in node.chain.blocks[-1].transactions:

                #node.account_space[trans.sender_address]['balance']=node.account_space[trans.sender_address]['valid_balance']

                flag = 1 if trans.type_of_transaction == 'coin' and (node.id != 0 or trans.nonce != 0) else 0 #bootstrap node isn't charged a fee when executing the genesis transactions
                if trans.receiver_address != '0': #regural transaction
                    node.account_space[trans.sender_address]['balance'] = node.account_space[trans.sender_address]['valid_balance'] - int(trans.to_dict()['amount']) * (1 + flag * 0.03)
                
                else: #transaction is stake(amount)
                    node.account_space[trans.sender_address]['balance'] += node.account_space[trans.sender_address]['valid_stake']
                    node.account_space[trans.sender_address]['stake'] = int(trans.to_dict()['amount'])
                    node.account_space[trans.sender_address]['balance'] -= node.account_space[trans.sender_address]['valid_stake']

                
                if trans.type_of_transaction != 'message': #regular transaction
                    node.account_space[trans.receiver_address]['balance'] += int(trans.to_dict()['amount'])

            validator = node.chain.blocks[-1].validator
            for pk in node.account_space:
                if pk == validator:
                    node.account_space[pk]['balance'] = node.account_space[pk]['valid_balance'] + fees_sum

                node.account_space[pk]['valid_balance'] = node.account_space[pk]['balance']
                node.account_space[pk]['valid_stake'] = node.account_space[pk]['stake']
 
            for ring_node in node.ring:
                if ring_node['public_key'] == validator:
                    await send_websocket_request('get_fees', {'fees':fees_sum},  ring_node['ip'], ring_node['port'])
                    break
            
            
            print(f"Node {node.id} received 'update_balance' action")

            await websocket.send(json.dumps({'message': "Balance updated"}))

        # elif data['action'] == 'update_soft_balance':


        elif data['action'] == 'update_ring':
            new_ring = data['data']
            node.ring = new_ring

            for ring_node in node.ring:
                if ring_node['ip']==node.ip and ring_node['port']==node.port:
                    node.id = ring_node['id']
                    break   
            # print(f"Node {node.id} received 'update_ring' action")

            await websocket.send(json.dumps({'message': "Ring updated"}))

        elif data['action'] == 'init_account_space':

            #Only run from non-bootstrap nodes
            for ring_node in node.ring:
                if ring_node['id'] == 0:
                    node.account_space[ring_node['public_key']] = {
                        'ip': ring_node['ip'],
                        'id': ring_node['id'],
                        'port': ring_node['port'],
                        'balance': 3000,
                        'valid_balance': 3000,
                        'stake': 0,
                        'valid_stake': 0
                    }
                else:
                    node.account_space[ring_node['public_key']] = {
                        'ip': ring_node['ip'],
                        'id': ring_node['id'],
                        'port': ring_node['port'],
                        'balance': 1000,
                        'valid_balance': 1000,
                        'stake': 0,
                        'valid_stake': 0
                    }
            await websocket.send(json.dumps({'message': "Account space initialized"}))

        elif data['action'] == 'update_chain':
           
            # Get the serialized chain from the other node
            serialized_chain = data['data']
            # Deserialize the chain
            chain = node.chain.from_dict(serialized_chain)
            node.chain = chain

            await websocket.send(json.dumps({'message': "Chain updated"}))

        elif data['action'] == 'stake':
            amount = data['data']['amount']
            await node.stake(amount)

            await websocket.send(json.dumps({'message': f"Pending stake: {amount}"}))

        elif data['action'] == 'get_stake':
            await websocket.send(json.dumps({'stake': node.stake_amount}))

        elif data['action'] == 'selected_as_validator':
    
            minting_time = await node.chain.mint_block(node)
              
            if minting_time != -1:
                await websocket.send(json.dumps({'minting_time': minting_time}))

            else:
                await websocket.send(json.dumps({'minting_time': '-1'}))

     
        
        elif data['action'] == 'update_block':
            transaction = data['data']

            #Update account state
            # print(node.account_space)

            if await node.validate_transaction(Transaction.from_dict(transaction)):

                flag = 1 if transaction['type_of_transaction'] == 'coin' and transaction['receiver_address'] != '0' else 0
                message_flag = 0 if transaction['type_of_transaction'] == 'message' else 1
                node.account_space[transaction['sender_address']]['balance'] -= transaction['amount'] * (1 + 0.03 * flag)
                node.account_space[transaction['recipient_address']]['balance'] += transaction['amount'] * message_flag

                
                # if transaction['recipient_address'] == node.wallet.public_key:
                #     transaction_recv = Transaction.from_dict(transaction)
                #     # print(f"Node {node.id} to receive: {transaction_recv.to_dict()['amount']}")
                #     node.transaction_pool.append(transaction_recv)

                # elif transaction['sender_address'] == node.wallet.public_key:
                #     transaction_send = Transaction.from_dict(transaction)
                #     # print(f"Node {node.id} to give: {transaction_send.to_dict()['amount']}")
                #     node.transaction_pool.append(transaction_send)

                transaction = Transaction.from_dict(transaction)
                node.transaction_pool.append(transaction)
                res = await node.add_transaction_to_block(transaction)

                # await websocket.send(json.dumps({'message':'Transaction added to block'}))

                if res['status'] == 200 and res['message'] == 'Block is full':
                    await send_websocket_request('mint_block', {}, node.ip, node.port)

                elif res['status'] == 200 and res['message'] == 'Transaction added to block':
                    await websocket.send(json.dumps({'message':'Transaction added to block'}))

                # elif res['status'] == 400:
                #     await websocket.send(json.dumps({'message':'Transaction Invalid'}))
                    
            else:
                
                await websocket.send(json.dumps({'message':'Transaction Invalid'}))
                
            # else:
            #     await websocket.send(json.dumps({'message':'Block is not full yet'}))



        elif data['action'] == 'mint_block':
           
            validator = await node.current_block.select_validator(node)

            await node.chain.mint_block(node)

            if node.id == validator['id']:

                await node.broadcast_block(node.current_block)
                await websocket.send(json.dumps({'message':'Block minted/Validator'}))

                for ring_node in node.ring:
                    await send_websocket_request('update_balance', {}, ring_node['ip'], ring_node['port'])
                
                for ring_node in node.ring:
                    await send_websocket_request('update_soft_balance', {}, ring_node['ip'], ring_node['port'])

            else:
                await websocket.send(json.dumps({'message':'Block minted/Not the validator'}))

           
            #     await websocket.send(json.dumps({'status':200,'message':'Block minted'}))
            # else:
            #     await websocket.send(json.dumps({'status':400,'message':'Block already minted'}))

        elif data['action'] == 'new_block':
            # if node.chain.blocks[-1].current_hash != data['data']['hash']:
            if node.validate_block(Block.from_dict(data['data'])):
                node.chain.add_block(Block.from_dict(data['data']))
                node.current_block = None   
                await websocket.send(json.dumps({'status':200,'message':'Block added to chain'}))

            else:
                await websocket.send(json.dumps({'status':400,'message':'Block Invalid'}))
           
     
        elif data['action'] == 'get_fees':

            fees = data['data']['fees']
            node.wallet.balance += fees

            await websocket.send(json.dumps({'message': "Fees received"}))



# Start the WebSocket server
async def main():
    async with websockets.serve(handler, IP_ADDRESS, PORT):
        print(f"Server started at ws://{IP_ADDRESS}:{PORT}")
        
        await register_node()  # Register the node with the bootstrap node
        await asyncio.Future()  # This will keep the server running indefinitely

# Run the server
if __name__ == "__main__":
    
    asyncio.run(main())

                


