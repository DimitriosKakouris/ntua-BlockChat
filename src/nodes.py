from blockchain import Blockchain
from transaction import Transaction
from wallet import Wallet
from block import Block
import websockets
import asyncio
import pickle
import json
from threading import Lock
from collections import deque



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

class Node:
    def __init__(self):
        self.chain = Blockchain()
        self.wallet = Wallet()
        self.ring = []
        self.id = None
        self.ip = None
        self.port = None
        self.transaction_pool = []
        self.stake = 0
        if self.chain.blocks:
                self.current_block = self.chain.blocks[-1]
        else:
                self.current_block = None  # Or create a new genesis block # Check if it is the correct way to handle current

        self.block_lock = Lock()
        # self.capacity = 5

    @classmethod
    def from_dict(cls, data):
        node = cls()
        node.chain = Blockchain.from_dict(data['chain'])
        node.wallet = Wallet.from_dict(data['wallet'])
        node.ring = data['ring']
        node.id = data['id']
        node.ip = data['ip']
        node.port = data['port']
        node.transaction_pool = deque(data['transaction_pool'])
        node.stake = data['stake']
        node.current_block = Block.from_dict(data['current_block'])
        node.block_lock = Lock()
        node.capacity = data['capacity']

        return node

       
    
    def stake(self, amount):
        """
        Updates the node's stake amount for the Proof of Stake process.
        The node can increase or decrease its stake, within the limits of its available balance.
        """
        stake_trasaction = self.create_transaction(self.wallet.public_key, "coin", amount)

        if not stake_trasaction["success"]:
            return False
        
        else:
            self.stake = amount
            return True
    

    def add_block(self, block):
        self.chain.add_block(block)
    
    def validate_block(self, block):
        return (block.previous_hash == self.chain.blocks[-1].current_hash) and (block.current_hash == block.hash_block())
    
    def validate_chain(self, blocks):
        """Validates all the blocks of a chain"""

        if (blocks[0].previous_hash != 1) or (blocks[0].hash != blocks[0].hash_block()):
            return False

        for i in range(1, len(blocks)):
            if not (blocks[i].hash == blocks[i].hash_block()) or not (blocks[i].previous_hash == blocks[i - 1].hash):
                return False
        return True
    
    def register_node_to_ring(self,id, ip, port, public_key):
        self.ring.append({
            "id": id,
            "ip": ip,
            "port": port,
            "public_key": public_key,
           
        })

    
    async def create_transaction(self, receiver_public_key, type_of_transaction, amount, message=None):
        """Creates a new transaction, directly adjusting account balances."""


        # Check if the account has enough balance:
        if self.wallet.balance < int(amount):
            return {"minting_time": 0, "success": False}

        ## REMOVED BALANCE CHECK FOR TESTING PURPOSES

        # Create the transaction
        transaction = Transaction(
            sender_address=self.wallet.public_key,
            #sender_id=self.id,
            receiver_address=receiver_public_key,
            #receiver_id=receiver_id,
            type_of_transaction=type_of_transaction,
            amount=amount,
            nonce=self.wallet.nonce,
            message=message
        )

        # Sign the transaction
        transaction.sign_transaction(self.wallet.private_key)

        # Broadcast transaction
        broadcast = await self.broadcast_transaction(transaction)
        print("Broadcast response:", broadcast)
        minting_time = broadcast["minting_time"]
        success = broadcast["success"]

        if not success:
            # If broadcasting fails, no need to revert anything in the account model
            return {"minting_time": minting_time, "success": False}

        self.wallet.nonce += 1
        return {"minting_time": minting_time, "success": True}
    


    async def share_ring(self, node):
        """
        ! BOOTSTRAP ONLY !
        Send the information about all the registered nodes 
        in the ring to a specific node using WebSockets.
        """

        await send_websocket_request('update_ring', self.ring, node['ip'], node['port'])

     

    async def share_chain(self, ring_node):
        """
        ! BOOTSTRAP ONLY !
        Send the information about all the registered nodes 
        in the ring to a specific node using WebSockets.
        """

        response = await send_websocket_request('update_chain', self.chain.to_dict(), ring_node['ip'], ring_node['port'])
     
        return response
    

    async def send_transaction(self, node, transaction):
        """Asynchronously sends a transaction to a single node via WebSocket."""
        response = await send_websocket_request('update_transaction_pool', transaction.to_dict(), node['ip'], node['port'])
        
        # Return the response
        return response

    async def broadcast_transaction(self, transaction):
        """Broadcasts a transaction to the network using WebSockets."""
        tasks = []
        responses = []

        for node in self.ring:
            if node['id'] != self.id:
                task = asyncio.create_task(self.send_transaction(node, transaction))
                tasks.append(task)

        for task in tasks:
            responses.append(await task)

        print("Responses:", responses)
        # Check responses for validation and receipt acknowledgment
        if not all(response.get('status') == 'OK' for response in responses):
            return {"minting_time": 0, "success": False}

        # Add transaction to block (assuming this is an async operation)
        minting_time = await self.add_transaction_to_block(transaction)
        return {"minting_time": minting_time, "success": True}
    

    async def send_block(self, node, block):
        """Asynchronously sends a block to a single node via WebSocket."""
        uri = f"ws://{node['ip']}:{node['port']}"
        async with websockets.connect(uri) as websocket:
            await websocket.send(pickle.dumps(block))
            response_status = await websocket.recv()
            return int(response_status)

    async def broadcast_block(self, block):
        """Broadcasts a block to the network using WebSockets."""
        tasks = []
        block_accepted = False

        for node in self.ring:
            if node['id'] != self.id:
                task = asyncio.create_task(self.send_block(node, block))
                tasks.append(task)

        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response == 200:
                block_accepted = True
                break  # Stop checking if any node accepts the block

        if block_accepted:
            async with self.chain_lock:
                if self.validate_block(block):
                    self.chain.blocks.append(block)

   
    async def unicast_node(self, bootstrap_node):
        """
        Sends information about self to the bootstrap node using WebSockets.
        """
        ws_url = f"ws://{bootstrap_node['ip']}:{bootstrap_node['port']}"
        node_info = {
            'action': 'register_node',
            'data': {
                'ip': self.ip,
                'port': self.port,
                'public_key': self.wallet.public_key
            }
        }
        print("I have unicasted to the bootstrap node")

        async with websockets.connect(ws_url) as websocket:
            # Send the registration information as a JSON string
            await websocket.send(json.dumps(node_info))
            
            # Wait for a response from the bootstrap node
            response = await websocket.recv()
            response_data = json.loads(response)

            if response_data['status'] == 'Entered the network':
                print("Node has been registered to the network")
               
            
            else:
                print("Initialization failed")

        
    
    async def add_transaction_to_block(self, transaction):
        """Adds a transaction to a block, check if minting is needed and update
        the wallet and balances of participating nodes"""

        # # Add transaction to the wallet of the sender and the receiver
        # if transaction.sender_address  == self.wallet.public_key:
        #     self.wallet.transactions.append(transaction)
        #     self.wallet.balance -= int(transaction.amount)

        
        # # # Does not work because it is not called by receiver
        # # if transaction.receiver_address == self.wallet.public_key:
        # #     self.wallet.transactions.append(transaction)
        # #     self.wallet.balance += int(transaction.amount)

        # # Update the balance of the sender and the receiver
        # print("In add_transaction_block ring: ", self.ring)
        # for ring_node in self.ring:
        #     print("In add_transaction_block loop", ring_node)
        #     print("In add_transaction_block loop receiver address", repr(transaction.receiver_address))
        #     print(repr(ring_node['public_key']))
        #     if ring_node['public_key'] == str(transaction.receiver_address):
        #         print(ring_node['public_key'])
        #         receiver_ip = ring_node['ip']
        #         receiver_port = ring_node['port']
        #         print(receiver_ip, receiver_port)
        
    
        # data={'amount':transaction.amount,'type_of_transaction':transaction.type_of_transaction}
        # await send_websocket_request('update_balance',data,receiver_ip, receiver_port)

        # If chain has only the genesis block, create new block
        if self.chain.size() == 1:
            self.current_block = Block(None, None)
            self.chain.add_block(self.current_block)

        self.block_lock.acquire()
        print("Block lock acquired")
        if self.current_block.add_transaction(transaction):
            self.block_lock.release()  # Release lock before minting
            validator = self.chain.select_validator(self.ring)

            if validator == self.wallet.public_key:
            # Mint the block if this node is the validator
                minting_time = self.chain.mint_block(self.current_block, self.capacity)
                for ring_node in self.ring:
                    await send_websocket_request('update_chain', self.chain.to_dict(), ring_node['ip'], ring_node['port'])
                    await send_websocket_request('update_balance', {}, ring_node['ip'], ring_node['port'])
            

                # Assume mint_block finalizes and broadcasts the block, returning the time it took
                self.current_block = None  # Reset current block after minting
                return minting_time
            else:
                # If not the validator, wait for the new block to be received
                return 0
        else:
            self.block_lock.release()
            return 0
