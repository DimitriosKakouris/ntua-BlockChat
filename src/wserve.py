import asyncio
import os
import json
import websockets
from dotenv import load_dotenv
from nodes import Node
from block import Block
from transaction import Transaction
from wsmanager import send_websocket_request
import execute_tests
import subprocess
import sys

lock = asyncio.Lock()

node = Node()

# Load environment variables and set up node details
load_dotenv()

result = subprocess.run(["hostname", "-I"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
ips = result.stdout.strip().split()
matched_ip = [i for i in ips if "10.110.0" in i]
IP_ADDRESS = matched_ip[0]
PORT = 80


total_nodes = int(os.getenv('TOTAL_NODES', 3))
block_capacity = int(os.getenv('BLOCK_CAPACITY', 5))
compute_justice_str = os.getenv("COMPUTE_JUSTICE", "False")
compute_justice = compute_justice_str == "True" #bool(os.getenv("COMPUTE_JUSTICE", False))

total_bcc = total_nodes * 1000
test_mode_str = os.getenv('TEST_MODE', "False")
test_mode = test_mode_str == 'True'

bootstrap_node = {
    'ip': os.getenv('BOOTSTRAP_IP', '10.110.0.2'),
    'port': os.getenv('BOOTSTRAP_PORT', '80')
}

# Debug prints
# print('IP address: ', IP_ADDRESS)
# print('PORT: ', PORT)

node.ip = IP_ADDRESS
node.port = str(PORT)



# See if node is Bootstrap node
if IP_ADDRESS == bootstrap_node["ip"] and str(PORT) == bootstrap_node["port"]:
    node.id = 0
    bootstrap_node = node
    print("I am bootstrap")


bootstrap_ready_event = asyncio.Event()
test_ready_event = asyncio.Event()
async def register_node():
   
        if node.id == 0:
            # Add himself to ring
            node.register_node_to_ring(node.id, node.ip, node.port, node.wallet.public_key)
            transaction = Transaction(
                sender_address='0',
                receiver_address=node.wallet.public_key,
                type_of_transaction='coin',
                amount=total_bcc,
                nonce=1,
                message=None
            )
            
          
            node.wallet.balance += total_bcc
            genesis_block = Block(1,'1')
            genesis_block.validator = 0
            genesis_block.transactions.append(transaction)
            await node.chain.add_block(genesis_block,node)
            print("Bootstrap node waiting for other nodes to be ready...")
            await bootstrap_ready_event.wait()
           
            print("Bootstrap node proceeding...")
            await send_init_bcc()
            print('After send_initial_bcc')

            await test_ready_event.wait()
            if test_mode:
                await execute_tests.execute_transactions(node.id, node.ip, node.port)

        else: 
            # Gather all unicast tasks
            unicast_tasks = [node.unicast_node(bootstrap_node), send_websocket_request('init_account_space', {}, node.ip, node.port)]
            await asyncio.gather(*unicast_tasks)

            data = await send_websocket_request('get_ring_length', {}, node.ip, node.port)
            print("Ring length: ", data['ring_len'])
            if data['ring_len'] == total_nodes: #TODO: may need better condition
                await send_websocket_request('last_node_ready', {}, bootstrap_node['ip'], bootstrap_node['port'])
              

            await test_ready_event.wait()
            if test_mode:
                await execute_tests.execute_transactions(node.id, node.ip, node.port)
             

    
async def send_init_bcc():
    print("Node ID in send initial: ", node.id)
    if node.id == 0:
        await node.send_initial_bcc()
        await asyncio.sleep(3)

        
        for ring_node in node.ring:
            asyncio.create_task(send_websocket_request('ready_for_tests', {}, ring_node['ip'], ring_node['port']))
                
        await send_websocket_request('ready_for_tests', {}, node.ip, node.port)
                
        


async def handler(websocket):
   

    async for message in websocket:
        data = json.loads(message)
        
        

        if data['action'] == 'last_node_ready':
            print("Last node is ready, proceeding...")
            bootstrap_ready_event.set()  # Signal the event
            await websocket.send(json.dumps({'message': "Last node is ready endpoint triggered"}))



        elif data['action'] == 'ready_for_tests':
            test_ready_event.set()
            await websocket.send(json.dumps({'message': "Tests event set"}))
         
        

        elif data['action'] == 'register_node':
            node_data = data['data']
        
            bootstrap_node.register_node_to_ring(len(bootstrap_node.ring), node_data['ip'], node_data['port'], node_data['public_key'])

            if len(bootstrap_node.ring) == total_nodes:
                
                for ring_node in bootstrap_node.ring:
                    if ring_node['id'] != 0:
                        await bootstrap_node.share_chain(ring_node)
                        await bootstrap_node.share_ring(ring_node)
                        await bootstrap_node.share_account_space(ring_node)
                        
                        
            await websocket.send(json.dumps({'status' : 'Node with id ' + str(len(bootstrap_node.ring)) + ' registered'}))

           
           

        elif data['action'] == 'new_transaction':
           
            receiver = data['data']['receiver']
            for ring_node in node.ring:
                if ring_node['id'] == int(receiver):
                    receiver = ring_node['public_key']
                    break

            amount = data['data']['amount']
          
            if await node.create_transaction(receiver, 'coin', amount):
              
                await websocket.send(json.dumps({'message': "Transaction created"}))
            else:
                await websocket.send(json.dumps({'message': "Transaction failed"}))

     
        elif data['action'] == 'new_message':
           
            receiver = data['data']['receiver']
            for ring_node in node.ring:
                if ring_node['id'] == int(receiver):
                    receiver = ring_node['public_key']
                    break

            
            message = data['data']['message']
            
            if await node.create_transaction(receiver, 'message', 0, message):
                await websocket.send(json.dumps({'message': "Message was registered"}))
            else:
                await websocket.send(json.dumps({'message': "Sending of the message failed"}))
        


        elif data['action'] == 'validate_transaction':
            new_transaction = data['transaction']
            if await node.validate_transaction(new_transaction):
                await websocket.send(json.dumps({'message': "OK"}))
            else:
                await websocket.send(json.dumps({'message': "The signature is not valid or not enough balance"}))


        elif data['action'] == 'get_balance':
            balance = node.account_space[node.wallet.public_key]['balance']
            stake_amount = node.account_space[node.wallet.public_key]['stake']
            confirmed_balance = node.wallet.balance
            confirmed_stake = node.stake_amount
            wallet_address = node.wallet.public_key
            node_id = node.id

            await websocket.send(json.dumps({'Node ID':node_id,'chain':node.chain.to_dict(),'wallet_address':wallet_address,'balance': balance, 'stake':stake_amount, 'confirmed_balance':confirmed_balance, 'confirmed_stake':confirmed_stake}))



        elif data['action'] == 'view_last_transactions':
            last_validated_block = node.chain.blocks[-1].view_block()
            await websocket.send(json.dumps(last_validated_block))



        elif data['action'] == 'view_last_messages':
            last_validated_block = node.chain.blocks[-1].view_block()
            messages = [transaction['message'] for transaction in last_validated_block['transactions'] if transaction['type_of_transaction'] == 'message' and transaction['recipient_address'] == node.wallet.public_key]
            await websocket.send(json.dumps(messages))
          


        elif data['action'] == 'get_ring_length':
            await websocket.send(json.dumps({'ring_len': len(node.ring)}))

   

        elif data['action'] == 'update_soft_state':
            node.account_space = data['data']
            print(f"Node {node.id} received 'update_soft_state' action")
            await websocket.send(json.dumps({'message': "Soft state updated"}))


        elif data['action'] == 'update_ring':
            new_ring = data['data']
            node.ring = new_ring

            for ring_node in node.ring:
                if ring_node['ip']==node.ip and ring_node['port']==node.port:
                    node.id = ring_node['id']
                    break   
          
            await websocket.send(json.dumps({'message': "Ring updated"}))



        elif data['action'] == 'init_account_space':

            #Only run from non-bootstrap nodes
            for ring_node in node.ring:
                if ring_node['id'] == 0:
                    node.account_space[ring_node['public_key']] = {
                        'ip': ring_node['ip'],
                        'id': ring_node['id'],
                        'port': ring_node['port'],
                        'balance': total_nodes * 1000,
                        'valid_balance': total_nodes * 1000,
                        'stake': 0,
                        'valid_stake': 0
                    }
                else:
                    node.account_space[ring_node['public_key']] = {
                        'ip': ring_node['ip'],
                        'id': ring_node['id'],
                        'port': ring_node['port'],
                        'balance': 0,
                        'valid_balance': 0,
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
            if await node.stake(amount):
                await websocket.send(json.dumps({'message': f"Pending stake: {amount}"}))
            else:
                await websocket.send(json.dumps({'message': "Failed to reserve amount for staking"}))



        elif data['action'] == 'get_stake':
            await websocket.send(json.dumps({'stake': node.stake_amount}))


     
        
        elif data['action'] == 'receive_transactions':
          
            transaction = data['data']
            print("I am in 'receive_transactions'")


            if node.current_block is None:
                node.current_block = Block(node.chain.blocks[-1].index + 1, node.chain.blocks[-1].current_hash)
       
            transaction = Transaction.from_dict(transaction)
            res = await node.add_transaction_to_block(transaction)

            
            if res['status'] == 200 and res['message'] == 'Block is full and going to mint':
                    # await node.mint_block()
                    await websocket.send(json.dumps(res))
            else:
                await websocket.send(json.dumps(res))
       

        


        elif data['action'] == 'new_block':
               
            async with node.chain.blockchain_lock:
                block = Block.from_dict(data['data'])
                validator = await Block.from_dict(data['data']).select_validator(node)

                print(f"##############THE VALIDATOR for {block.index} IS {validator['id']}##############")
                print(f"##############PREVIOUS HASH: {node.chain.blocks[-1].current_hash[:20]}##############")
                
                if block.index > len(node.chain.blocks)+1:
                # If the block's index is higher than the blockchain length, add it to the buffer
                    node.block_buffer[block.index] = block
                    print(f"##############BLOCK with {block.index} BUFFERED##############")


                else:
                    if await node.validate_block(block):
                        print(f"########### NEW BLOCK RECEIVED with index {block.index} ###########")
                        buff_blocks_added = await node.chain.add_block(block,node)
                        buff_blocks_added.append(data['data'])

                        for buff_block in buff_blocks_added:    
                            await node.update_final_soft_state(buff_block)

                       

                    
                        node.current_block = Block(node.chain.blocks[-1].index + 1, node.chain.blocks[-1].current_hash)
                        
                        node.new_block_event.set()

                    
                        # for _ in range(block_capacity-1):
                        #     if not node.pending_transactions:
                        #         break
                        #     trans = node.pending_transactions.popleft()
                        #     res = node.current_block.add_transaction(trans)
                         
                            # print(f"@@@@@@@@@RES from pushing pending transactions: {res} @@@@@@@@@ with current block validator {node.current_block.validator}")
                          

                        await websocket.send(json.dumps({'status':200,'message':'Block added to chain', 'pk':node.wallet.public_key ,'new_balance':node.wallet.balance , 'new_stake':node.stake_amount}))



                    else:
                        if block.previous_hash != node.chain.blocks[-1].current_hash:
                            print(f"#########BLOCK INVALID - HASH MISMATCH ###########")

                        elif block.validator != (validator['pk']):
                            print(f"#########BLOCK INVALID VALIDATOR PROBLEM INDEX {block.index} ###########")
                            
                            print(f"Expected validator: {validator['pk']} but got {block.validator} ########")
                    
                        await websocket.send(json.dumps({'status':400,'message':'Block Invalid'}))

    
      
                
        
        elif data['action'] == 'get_block_timestamps':
            timestamps = [block.timestamp for block in node.chain.blocks]
            # timestamps = [block.current_hash[:20] for block in node.chain.blocks]
            await websocket.send(json.dumps({'blocks':timestamps}))

        # elif data['action'] == 'shutdown':
        #     await websocket.send(json.dumps({'message': "Shutting down..."}))
        #     # websocket.close()
        #     # sys.exit(0)
        #     try:
        #         # Improved grep pattern to avoid matching the grep process itself
        #         command = ["pgrep", "-f", "python ./src/wserve.py"]
        #         result = subprocess.run(command, check=True, stdout=subprocess.PIPE, text=True)
        #         pid = result.stdout.strip()
        #         if pid:
        #             # Attempting graceful shutdown first
        #             subprocess.run(["kill", pid])
        #             # Consider adding a delay and check if the process is still running, then use SIGKILL
        #     except subprocess.CalledProcessError as e:
        #         # Handle errors such as no process found
        #         print(f"Error: {e}")
        #     except IndexError:
        #         print("Process ID not found. Is the process running?")




# Start the WebSocket server

async def main():

    asyncio.create_task(node.process_pending_transactions())
    async with websockets.serve(handler, IP_ADDRESS, PORT,ping_interval=None):
        print(f"Server started at ws://{IP_ADDRESS}:{PORT}")
        
        await register_node()  # Register the node with the bootstrap node
     
        await asyncio.Future()  # This will keep the server running indefinitely

# Run the server
if __name__ == "__main__":
    asyncio.run(main())

                


