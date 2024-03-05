from blockchain import Blockchain
from transaction import Transaction
from wallet import Wallet
from block import Block
from wsmanager import send_websocket_request
import asyncio
from threading import Lock



class Node:
    def __init__(self):
        self.chain = Blockchain()
        self.wallet = Wallet()
        self.ring = []
        self.id = None
        self.ip = None
        self.port = None
        self.transaction_pool = []
        self.stake_amount = 0
        self.current_block = None
        self.node_lock = Lock()
        # self.chain_lock = Lock()
       



    @classmethod
    def from_dict(cls, data):
        node = cls()
        node.chain = Blockchain.from_dict(data['chain'])
        node.wallet = Wallet.from_dict(data['wallet'])
        node.ring = data['ring']
        node.id = data['id']
        node.ip = data['ip']
        node.port = data['port']
        node.transaction_pool = data['transaction_pool']
        node.stake_amount = data['stake_amount']
        node.current_block = Block.from_dict(data['current_block'])
        node.block_lock = Lock()
        node.chain_lock = Lock()
     
        return node

       
    
    async def stake(self, amount):
        """
        Updates the node's stake amount for the Proof of Stake process.
        The node can increase or decrease its stake, within the limits of its available balance.
        """
        await self.create_transaction('0', "coin", amount)

        # if not stake_trasaction["success"]:
        #     return False
        
        # else:
        #     #self.stake = amount
        #     return True
    

    async def validate_transaction(self,transaction):
        """
        Validate the transaction.
        """
        if not transaction.verify_signature():
            return False
        
        # Check if the sender has enough balance
        
        # sender_ip = [ring_node['ip'] for ring_node in self.ring if ring_node['public_key'] == transaction.sender_address][0]
        # sender_port = [ring_node['port'] for ring_node in self.ring if ring_node['public_key'] == transaction.sender_address][0]
        # res = await send_websocket_request('get_balance', {}, sender_ip, sender_port)

        # if res['balance'] < int(transaction.amount):
        #     return False
        return True
        
    def validate_block(self, block):
        return (block.previous_hash == self.chain.blocks[-1].current_hash)
    
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

        # # Check if the account has enough balance:
        # if type_of_transaction == 'coin' and self.wallet.balance < int(amount):
        #     return {"Not enough balance"}
        # elif type_of_transaction == 'message' and self.wallet.balance < len(message):
        #     return {"Not enough balance"}

        # Create the transaction
        transaction = Transaction(
            sender_address=self.wallet.public_key,
            receiver_address=receiver_public_key,
            type_of_transaction=type_of_transaction,
            amount=amount,
            nonce=self.wallet.nonce,
            message=message
        )

        # Sign the transaction
        transaction.sign_transaction(self.wallet.private_key)
        # Broadcast transaction
        await self.broadcast_transaction(transaction)
       

        self.wallet.nonce += 1
       
    


    async def share_ring(self, node):
        """
        ! BOOTSTRAP ONLY !
        Send the information about all the registered nodes 
        in the ring to a specific node using WebSockets.
        """

        await send_websocket_request('update_ring', self.ring,  node['ip'], node['port'])

     

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
        response = await send_websocket_request('update_block', transaction.to_dict(),  node['ip'], node['port'])
        
        return response

    async def broadcast_transaction(self, transaction):
        """Broadcasts a transaction to the network using WebSockets."""
        tasks = []
        responses = []

        for node in self.ring:
                task = asyncio.create_task(self.send_transaction(node, transaction))
                tasks.append(task)

        for task in tasks:
            responses.append(await task)

        # print("Responses:", responses)

     
        await send_websocket_request('update_balance', {},  self.ip, self.port)
        # # Check responses for validation and receipt acknowledgment
      

    async def send_block(self, node, block):
        res = await send_websocket_request('new_block', block.to_dict(),  node['ip'], node['port'])
        return res
    
    async def broadcast_block(self, block):
        """Broadcasts a block to the network using WebSockets."""
        tasks = []
      

        for node in self.ring:
                task = asyncio.create_task(self.send_block(node, block))
                tasks.append(task)

        responses = await asyncio.gather(*tasks)
        print("Responses:", responses)

        for response in responses:
            if response['status'] == 200:
               
            #    print("Block accepted by the network")
               for ring_node in self.ring:
                    await send_websocket_request('update_balance', {},  ring_node['ip'], ring_node['port'])
                    
               break
            
            else:
                # print("Block rejected by the network")
                break
                    

   
    async def unicast_node(self, bootstrap_node):
        """
        Sends information about self to the bootstrap node using WebSockets.
        """
        node_info = {
                'ip': self.ip,
                'port': self.port,
                'public_key': self.wallet.public_key
        }
        response = await send_websocket_request('register_node', node_info, bootstrap_node['ip'], bootstrap_node['port'])
        # print("I have unicasted to the bootstrap node")

        # if response['status'] == 'Entered the network':
        #     print("Node has been registered to the network")
            
        
        # else:
        #     print("Initialization failed")

        
    
    async def add_transaction_to_block(self, transaction):
        """Adds a transaction to a block, check if minting is needed and update
        the wallet and balances of participating nodes"""

        # If chain has only the genesis block, create new block
        if self.current_block is None:
           
            self.current_block = Block(
            index=self.chain.blocks[-1].index + 1 ,
            previous_hash=self.chain.blocks[-1].current_hash,
            )
        
        if await self.validate_transaction(transaction):

            if self.current_block.add_transaction(transaction):

                validator = await self.current_block.select_validator(self.ring)  
                with self.node_lock:
                    res = await send_websocket_request('selected_as_validator', {'index':str(self.current_block.index)},  validator['ip'], validator['port'])
                    minting_time = res['minting_time'] 
            
            
                return minting_time
                            


   
