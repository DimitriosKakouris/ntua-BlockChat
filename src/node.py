from blockchain import Blockchain
from transaction import Transaction
from wallet import Wallet
from block import Block, genesis
from main import num_nodes

import websockets
import asyncio
import pickle
import json
from threading import Lock
from collections import deque


class Node:
    def __init__(self, id):
        self.chain = Blockchain()
        self.wallet = Wallet()
        self.ring = []
        self.id = id
        self.unconfirmed_transactions = deque()
        self.stake = 0

        self.block_lock = Lock()
        self.capacity = 5

    def stake(self, amount):
        """
        Updates the node's stake amount for the Proof of Stake process.
        The node can increase or decrease its stake, within the limits of its available balance.
        """
        stake_trasaction = self.create_transaction('0', "coin", amount)

        if not stake_trasaction["success"]:
            return False
        
        else:
            self.stake = amount
            return True
        
    def create_new_block(self):
        """Creates a new block"""
        
        if len(self.chain.blocks) == 0:
            # Genesis block
            self.current_block = genesis(self.wallet.public_key, num_nodes)
        else:
            # Filled out later
            self.current_block = Block(None, None)
        return self.current_block


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
    
    def register_node_to_ring(self, id, ip, port, public_key, balance):
        self.ring.append({
            "id": id,
            "ip": ip,
            "port": port,
            "public_key": public_key,
            "balance": balance
        })

    def create_transaction(self, receiver_public_key, type_of_transaction, amount, message=None):
        """Creates a new transaction, directly adjusting account balances."""

        # Check if the account has enough balance:
        if self.wallet.balance < amount:
            return {"minting_time": 0, "success": False}

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
        broadcast = self.broadcast_transaction(transaction)
        minting_time = broadcast["minting_time"]
        success = broadcast["success"]

        if not success:
            # If broadcasting fails, no need to revert anything in the account model
            return {"minting_time": minting_time, "success": False}

        # Deduct the amount from the sender's balance: this is done in add_transaction_to_block()
        # self.wallet.balance -= amount

        # In a real application, the receiver's balance would be updated when the transaction is confirmed,
        # not here. This line is for illustration only.
        # receiver_account.balance += amount
        self.wallet.nonce += 1
        return {"minting_time": minting_time, "success": True}
    

    async def send_transaction(self, node, transaction):
        """Asynchronously sends a transaction to a single node via WebSocket."""
        uri = f"ws://{node['ip']}:{node['port']}"
        async with websockets.connect(uri) as websocket:
            # Serialize and send the transaction
            await websocket.send(pickle.dumps(transaction))
            response = await websocket.recv()
            return json.loads(response)

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

        # Check responses for validation and receipt acknowledgment
        if not all(response['status'] == 'success' for response in responses):
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
    

    
    def add_transaction_to_block(self, transaction):
        """Adds a transaction to a block, check if minting is needed and update
        the wallet and balances of participating nodes"""

        # Add transaction to the wallet of the sender and the receiver
        if transaction.sender_address  == self.wallet.public_key:
            self.wallet.transactions.append(transaction)
        if transaction.receiver_address == self.wallet.public_key:
            self.wallet.transactions.append(transaction)

        # Update the balance of the sender and the receiver
        for ring_node in self.ring:
            if ring_node['public_key'] == transaction.sender_address:
                ring_node['balance'] -= transaction.amount
            if ring_node['public_key'] == transaction.receiver_address:
                ring_node['balance'] += transaction.amount

        # If chain has only the genesis block, create new block
        if self.current_block is None:
            self.current_block = self.create_new_block()

        self.block_lock.acquire()
        if self.current_block.add_transaction(transaction, self.capacity):
            self.block_lock.release()  # Release lock before minting
            validator = self.chain.select_validator(self.ring)

            if validator == self.wallet.public_key:
            # Mint the block if this node is the validator
                minting_time = self.chain.mint_block(self.current_block, self.capacity)
                # Assume mint_block finalizes and broadcasts the block, returning the time it took
                self.current_block = None  # Reset current block after minting
                return minting_time
            else:
                # If not the validator, wait for the new block to be received
                return 0
        else:
            self.block_lock.release()
            return 0
