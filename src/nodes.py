from blockchain import Blockchain
from transaction import Transaction
from wallet import Wallet
from block import Block
from wsmanager import send_websocket_request, send_websocket_request_unique, send_websocket_request_update
import asyncio
import os
from dotenv import load_dotenv
import time

load_dotenv()
total_nodes = int(os.getenv('TOTAL_NODES', 5))


class Node:
    def __init__(self):
        self.chain = Blockchain()
        self.wallet = Wallet()
        self.ring = []
        self.id = None
        self.ip = None
        self.port = None
        self.current_block = None
        self.transaction_pool = []
        self.stake_amount = 0
        self.account_space = {}
      
       



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
      
     
        return node

    

    async def stake(self, amount):
        """
        Updates the node's stake amount for the Proof of Stake process.
        The node can increase or decrease its stake, within the limits of its available balance.
        """
        return await self.create_transaction('0', "coin", amount)

 

    async def validate_transaction(self,transaction):
        """
        Validate the transaction.
        """
        print("I am in 'validate_transaction'")
        if not transaction.verify_signature():
            return False
        
    
        sender_balance = self.account_space[transaction.sender_address]['balance']

        flag = 1 if transaction.type_of_transaction == 'coin' and (int(self.account_space[transaction.sender_address]['id'])!= 0 or transaction.nonce >= len(self.ring) ) else 0
        stake_flag = 1 if transaction.receiver_address == '0' else 0
        if int(transaction.amount) * (1 + flag * 0.03)  > int(sender_balance) + int(self.account_space[transaction.sender_address]['stake']) * stake_flag:
            return False
    
     
        return True
        
    async def validate_block(self, block):
    
        validator = await block.select_validator(self)
    
        return (block.previous_hash == self.chain.blocks[-1].current_hash) and (block.validator == validator['pk'])
    

    def validate_chain(self, blocks):
        """Validates all the blocks of a chain"""

        if (blocks[0].previous_hash != 1) or (blocks[0].hash != blocks[0].hash_block()):
            return False

        for i in range(1, len(blocks)):
            if not (blocks[i].hash == blocks[i].hash_block()) or not (blocks[i].previous_hash == blocks[i - 1].hash):
                return False
        return True
    
    def register_node_to_ring(self,id, ip, port, public_key):
        print("In register_node_to_ring, node id:", id)
        self.ring.append({
            "id": id,
            "ip": ip,
            "port": port,
            "public_key": public_key,
           
        })

        if self.id == id:
            self.account_space[public_key] = {
                'id' : id,
                "ip": ip,
                "port": port,
                "balance": total_nodes * 1000,
                #"valid_balance":3000,
                "stake": 0,
                #"valid_stake": 0
            }
        else:
            self.account_space[public_key] = {
                'id' : id,
                "ip": ip,
                "port": port,
                #"balance": 1000,
                "balance": 0,
                "stake": 0,
            }

    
    async def create_transaction(self, receiver_public_key, type_of_transaction, amount, message=None):
        """Creates a new transaction, directly adjusting account balances."""

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
        res = await self.broadcast_transaction(transaction)
        

        if res['valid']:
            self.wallet.nonce += 1
            return True
        
        else:
            print("Invalid transaction")
            return False
             
            

    async def send_initial_bcc(self):
        print("Ring:", self.ring)
        for ring_node in self.ring:
            if ring_node['id'] != 0:
                if await self.create_transaction(ring_node['public_key'],'coin',1000):
                    print(f"Node {ring_node['id']} successfully received 1000 BCCs")




    async def update_balance(self):
        transaction_pool_copy = self.transaction_pool.copy()
        for trans in transaction_pool_copy:
            if any(trans.transaction_id == transaction.transaction_id for transaction in self.chain.blocks[-1].transactions):
                
                flag = 1 if trans.type_of_transaction == 'coin' and (self.account_space[trans.sender_address]['id']!= '0' or trans.nonce >= len(self.ring)) else 0 #bootstrap node isn't charged a fee when executing the genesis transactions
                
                if self.chain.blocks[-1].validator == self.wallet.public_key:
                    if trans.type_of_transaction == 'coin' and trans.receiver_address != '0':
                        self.wallet.balance += flag * 0.03 * int(trans.to_dict()['amount'])
                    elif trans.type_of_transaction == 'message':
                        self.wallet.balance += int(trans.to_dict()['amount'])
                
                if trans.sender_address == self.wallet.public_key and trans.receiver_address != '0': #regural transaction
                    self.wallet.balance -= int(trans.to_dict()['amount']) * (1 + flag * 0.03)
                
                elif trans.sender_address == self.wallet.public_key and trans.receiver_address == '0': #transaction is stake(amount)
                    self.wallet.balance += self.stake_amount
                    self.stake_amount = int(trans.to_dict()['amount'])
                    self.wallet.balance -= self.stake_amount

                if trans.receiver_address == self.wallet.public_key:
                    if trans.type_of_transaction == 'coin': #regular transaction
                        self.wallet.balance += int(trans.to_dict()['amount'])
                    
                # Remove the transaction from the original transaction_pool
                self.transaction_pool.remove(trans)
        
        if self.chain.blocks[-1].validator == self.wallet.public_key:
            self.account_space[self.wallet.public_key]['balance'] = self.wallet.balance
    

    async def update_soft_state(self,fees_sum):
        validator = self.chain.blocks[-1].validator
        for ring_node in self.ring:
            if ring_node['public_key'] == validator and ring_node['id'] != self.id:

                # await send_websocket_request('get_fees', {'fees':fees_sum}, ring_node['ip'], ring_node['port'])
                break

            if self.wallet.public_key == validator: 
                self.wallet.balance += fees_sum



            #     # For fetching balances concurrently and updating account_space
            # get_balance_tasks = [
            #     send_websocket_request('get_balance', {}, ring_node['ip'], ring_node['port']) 
            #     for ring_node in self.ring
            # ]
            # balances = await asyncio.gather(*get_balance_tasks)
                balances = 100
            
            print('async get_balance_tasks successful')

            for ring_node, balance in zip(self.ring, balances):
                self.account_space[ring_node['public_key']]['balance'] = balance['balance']
                self.account_space[ring_node['public_key']]['stake'] = balance['stake']
            

            self.current_block = None   


    
       
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
    

    async def share_account_space(self, ring_node):

        response = await send_websocket_request('init_account_space', {}, ring_node['ip'], ring_node['port'])
        return response
    

    async def send_transaction(self, node, transaction):
        """Asynchronously sends a transaction to a single node via WebSocket."""
        print("I am in 'send_transaction'")
        # if self.id == node['id']:
            # response = await send_websocket_request_self_update('update_block', transaction.to_dict(), self.ip, self.port)
        # else:
        response = await send_websocket_request_update('update_block', transaction.to_dict(),  node['ip'], node['port'])
        
        return response

    async def broadcast_transaction(self, transaction):
        """Broadcasts a transaction to the network using WebSockets."""
      

        for node in self.ring :
                if self.id != node['id']:
         
                     asyncio.create_task(self.send_transaction(node, transaction))
         
                
        for node in self.ring:
            if self.id == node['id']:
                 response = await self.send_transaction(node, transaction)

       
        print("Response from self:", response)  

        if response["message"] == "Transaction Invalid" :
            
            return {'valid': False}
        
        elif response["message"] == "Transaction added to block" :
            return {'valid': True,'full': False}
        
       
        elif response["message"] == "Block is full" :
            return {'valid': True,'full': True}
      

    async def send_block(self, node, block):
   
        res= await send_websocket_request_unique('new_block', block.to_dict(), node['ip'], node['port'])
     
        return res
    

    async def broadcast_block(self, block):
        """Broadcasts a block to the network using WebSockets."""
     
        for node in self.ring:
            if node['id'] != self.id:
                asyncio.create_task(self.send_block(node, block))
            else:
                response = await self.send_block(node, block)

    
        print("Responses from self:", response)


        for ring_node in self.ring:
            if ring_node['id'] != self.id:
                await send_websocket_request('update_soft_state', self.account_space, ring_node['ip'], ring_node['port'])
        return True
            

   
    async def unicast_node(self, bootstrap_node):
        """
        Sends information about self to the bootstrap node using WebSockets.
        """
        node_info = {
                'ip': self.ip,
                'port': self.port,
                'public_key': self.wallet.public_key
        }
        await send_websocket_request('register_node', node_info, bootstrap_node['ip'], bootstrap_node['port'])
        # print("I have unicasted to the bootstrap node")

        # if response['status'] == 'Entered the network':
        #     print("Node has been registered to the network")
            
        
        # else:
        #     print("Initialization failed")

    async def mint_block(self):
        validator = await self.current_block.select_validator(self)

        await self.chain.mint_block(self)

        if self.id == validator['id']:
        
            # self.wallet.balance = self.account_space[self.wallet.public_key]['balance']
            # self.stake_amount = self.account_space[self.wallet.public_key]['stake']

            await self.broadcast_block(self.current_block)
            #new_timestamp = time.time()
    
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
               return {'status': 200, 'message': 'Block is full'}
            
            else:
                return {'status': 200, 'message': 'Transaction added to block'}
      

                # validator = await self.current_block.select_validator(self.ring)  
                # with self.node_lock:
                #     res = await send_websocket_request('selected_as_validator', {'index':str(self.current_block.index)},  validator['ip'], validator['port'])
                #     minting_time = res['minting_time'] 
            
        print(transaction.to_dict())
        return {'status': 400, 'message': "Transaction couldn't be added to block"}
                # return minting_time
                            


   
