from blockchain import Blockchain
from transaction import Transaction
from wallet import Wallet
from block import Block
from wsmanager import send_websocket_request, send_websocket_request_unique, send_websocket_request_update
import asyncio
import os
from dotenv import load_dotenv
from collections import deque

load_dotenv()
total_nodes = int(os.getenv('TOTAL_NODES', 5))
block_capacity = int(os.getenv('BLOCK_CAPACITY', 5))

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
        self.pending_transactions = deque()
        self.block_buffer = {}
        
    

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
            # print(f"Insufficient balance {int(sender_balance) + int(self.account_space[transaction.sender_address]['stake']) * stake_flag} and amount {int(transaction.amount) * (1 + flag * 0.03)}")
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
                "valid_balance": total_nodes * 1000,
                "stake": 0,
                "valid_stake": 0
            }
        else:
            self.account_space[public_key] = {
                'id' : id,
                "ip": ip,
                "port": port,
                "balance": 0,
                "valid_balance": 0,
                "stake": 0,
                "valid_stake": 0
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




    # async def update_balance(self, transactions): #, transactions
    #     #async with self.block_lock:
    #     buffer_deque = deque()
    #     transactions_copy = transactions.copy()
        

    #     for trans in transactions_copy:
          
    #         flag = 1 if trans.type_of_transaction == 'coin' and (self.account_space[trans.sender_address]['id']!= '0' or trans.nonce >= total_nodes-1) else 0

    #         if self.chain.blocks[-1].validator == self.wallet.public_key:
    #             if trans.type_of_transaction == 'coin' and trans.receiver_address != '0':
    #                 self.wallet.balance += flag * 0.03 * int(trans.to_dict()['amount'])
    #                 # self.account_space[self.wallet.public_key]['balance'] += flag * 0.03 * int(trans.to_dict()['amount'])
    #             elif trans.type_of_transaction == 'message':
    #                 self.wallet.balance += int(trans.to_dict()['amount'])
    #                 # self.account_space[self.wallet.public_key]['balance'] += int(trans.to_dict()['amount'])

    #         if trans.sender_address == self.wallet.public_key and trans.receiver_address != '0':
    #             self.wallet.balance -= int(trans.to_dict()['amount']) * (1 + flag * 0.03)

    #         elif trans.sender_address == self.wallet.public_key and trans.receiver_address == '0':
    #             print("I am in 'update_balance' for stake")
    #             self.wallet.balance += self.stake_amount
    #             self.stake_amount = int(trans.to_dict()['amount'])
    #             self.wallet.balance -= self.stake_amount

    #         if trans.receiver_address == self.wallet.public_key and trans.type_of_transaction == 'coin':
    #             self.wallet.balance += int(trans.to_dict()['amount'])
    #         # else:
    #         #     buffer_deque.append(trans)
        
    #     while self.pending_transactions:
    #         trans = self.pending_transactions.popleft()
    #         if trans not in transactions_copy:
    #             buffer_deque.append(trans)
    #     while buffer_deque:
    #         self.pending_transactions.appendleft(buffer_deque.pop())

        


    async def update_soft_state(self,transaction):
        #async with self.block_lock: #and transaction['recipient_address'] != '0' 
        print("I am in 'update_soft_state'")
        flag = 1 if transaction['type_of_transaction'] == 'coin' and (self.account_space[transaction['sender_address']]['id'] != 0 or transaction['nonce'] >= len(self.ring) ) else 0
        message_flag = 0 if transaction['type_of_transaction'] == 'message' else 1

        if transaction['recipient_address'] != '0':
            self.account_space[transaction['sender_address']]['balance'] -= int(transaction['amount']) * (1 + 0.03 * flag)
            self.account_space[transaction['recipient_address']]['balance'] += int(transaction['amount']) * message_flag

        else:
            print("I am in 'update_soft_state' for stake")
            self.account_space[transaction['sender_address']]['balance'] += self.account_space[transaction['sender_address']]['stake']
            self.account_space[transaction['sender_address']]['stake'] = int(transaction['amount'])
            self.account_space[transaction['sender_address']]['balance'] -= self.account_space[transaction['sender_address']]['stake']
            
    async def update_final_soft_state(self, block_info):
        print("Block info:", block_info)
        transactions = block_info['transactions']
        validator = block_info['validator']
       
        for transaction in transactions:
            print(transaction)
            flag = 1 if transaction['type_of_transaction'] == 'coin' and (self.account_space[transaction['sender_address']]['id'] != 0 or transaction['nonce'] >= total_nodes ) else 0
            message_flag = 0 if transaction['type_of_transaction'] == 'message' else 1

            if transaction['recipient_address'] != '0':
                self.account_space[transaction['sender_address']]['valid_balance'] -= int(transaction['amount']) * (1 + 0.03 * flag)
                self.account_space[transaction['recipient_address']]['valid_balance'] += int(transaction['amount']) * message_flag
                if transaction['type_of_transaction'] == 'coin':
                    self.account_space[validator]['valid_balance'] += 0.03 * flag * int(transaction['amount'])
                else:
                    self.account_space[validator]['valid_balance'] += int(transaction['amount'])

            else:
                print("I am in 'update_final_soft_state' for stake")
                self.account_space[transaction['sender_address']]['valid_balance'] += self.account_space[transaction['sender_address']]['valid_stake']
                self.account_space[transaction['sender_address']]['valid_stake'] = int(transaction['amount'])
                self.account_space[transaction['sender_address']]['valid_balance'] -= self.account_space[transaction['sender_address']]['valid_stake']
        
        for i in self.account_space.keys():
            self.account_space[i]['balance'] = self.account_space[i]['valid_balance']
            self.account_space[i]['stake'] = self.account_space[i]['valid_stake']
        self.wallet.balance = self.account_space[self.wallet.public_key]['valid_balance']
        self.stake_amount = self.account_space[self.wallet.public_key]['valid_stake']


        blockchain_transactions = {trans.transaction_id for block in self.chain.blocks for trans in block.transactions}

        # Convert block_info['transactions'] to a set of dictionaries and add it to blockchain_transactions
        block_info_transactions = {trans['transaction_id'] for trans in block_info['transactions']}
        blockchain_transactions.update(block_info_transactions)

        buffer_deque = deque()
        while self.pending_transactions:
            trans = self.pending_transactions.popleft()
            trans_id = trans.transaction_id
            if trans_id not in blockchain_transactions:
                buffer_deque.append(trans)
        while buffer_deque:
            self.pending_transactions.appendleft(buffer_deque.pop())

       
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
        self.current_block = Block(self.chain.blocks[-1].index + 1, self.chain.blocks[-1].current_hash)
        return response
    



    async def share_account_space(self, ring_node):

        response = await send_websocket_request('init_account_space', {}, ring_node['ip'], ring_node['port'])
        return response
    



    async def send_transaction(self, node, transaction):
        """Asynchronously sends a transaction to a single node via WebSocket."""
        print("I am in 'send_transaction'")
      
        response = await send_websocket_request_update('receive_transactions', transaction.to_dict(),  node['ip'], node['port'])
        
        return response





    async def broadcast_transaction(self, transaction):
        """Broadcasts a transaction to the network using WebSockets."""
      

        for node in self.ring :
                if self.id != node['id']:
                     asyncio.create_task(self.send_transaction(node, transaction))
         
                
        response = await self.receive_transactions(transaction.to_dict())

       
        print("Response from self:", response)  

        if response["message"] == "Transaction Invalid":
            
            return {'valid': False}
        
        else:
            return {'valid': True}
        


    async def send_block(self, node, block):
        
        res = await send_websocket_request_unique('new_block', block.to_dict(), node['ip'], node['port'])
     
        return res
    

    async def broadcast_block(self, block):
        """Broadcasts a block to the network using WebSockets."""
     
        for node in self.ring:
                if node['id'] != self.id:
                    asyncio.create_task(self.send_block(node, block))
          
        
        response = await self.new_block(block.to_dict())

    
        print("Responses from self broadcast_block:", response)

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
      


      
    async def mint_block(self):

        self.chain.mint_block(self)
        async with self.chain.blockchain_lock:
            validator = await self.current_block.select_validator(self)
        
        block_to_be_broadcasted = self.current_block
      
        
        if self.id == validator['id']:
            print(f"I {self.id} am the validator, and I am broadcasting block {block_to_be_broadcasted.index}")
            await self.broadcast_block(block_to_be_broadcasted)
  




    async def add_transaction_to_block(self, transaction):
        """Adds a transaction to a block, check if minting is needed and update
        the wallet and balances of participating nodes"""

        transaction_added = self.current_block.add_transaction(transaction)

        if transaction_added == 2:
            self.pending_transactions.append(transaction)


            if self.current_block.validator is None:
                return {'status': 200, 'message': 'Block is full and going to mint'}
            else:
                return {'status': 200, 'message': 'Block is full and already minted'}

        elif transaction_added == 1:
            if not await self.validate_transaction(transaction):
                self.current_block.transactions.pop()
                return {'status': 400, 'message': 'Transaction Invalid'}
            
            if self.current_block.validator is None:
                return {'status': 200, 'message': 'Block is full and going to mint'}
            else:
                return {'status': 200, 'message': 'Block is full and already minted'}


        
        elif transaction_added == 0:
            if not await self.validate_transaction(transaction):
                self.current_block.transactions.pop()
                return {'status': 400, 'message': 'Transaction Invalid'}
            
            await self.update_soft_state(transaction.to_dict())
         
            print(f"Transaction added to block and curr length is {len(self.current_block.transactions)}")
            return {'status': 200, 'message': 'Transaction added to block'}
  
      


   
    async def receive_transactions(self, data):
        transaction = data
        print("I am in 'receive_transactions'")

        if self.current_block is None:
            self.current_block = Block(self.chain.blocks[-1].index + 1, self.chain.blocks[-1].current_hash)

        try:

              
            transaction = Transaction.from_dict(transaction)
            res = await self.add_transaction_to_block(transaction)

            
            if res['status'] == 200 and res['message'] == 'Block is full and going to mint':
                await self.mint_block()
                return res
    
            return res
              
        
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return {'valid': False, 'message': 'An error occurred'}
        



    async def new_block(self,data):
      
       
        async with self.chain.blockchain_lock:
            block = Block.from_dict(data)
            validator = await Block.from_dict(data).select_validator(self)
            print(f"##############THE VALIDATOR for {block.index} IS {validator['id']}##############")
            print(f"##############PREVIOUS HASH: {self.chain.blocks[-1].current_hash[:20]}##############")
            
            if block.index > len(self.chain.blocks)+1:
            # If the block's index is higher than the blockchain length, add it to the buffer
                self.block_buffer[block.index] = block
                print(f"##############BLOCK with {block.index} BUFFERED##############")
                


            else:
                if await self.validate_block(block):
                    print(f"########### NEW BLOCK RECEIVED with index {block.index} ###########")
                   
                    buff_blocks_added = await self.chain.add_block(block,self)
                    buff_blocks_added.append(data)

                    for buff_block in buff_blocks_added:    
                        await self.update_final_soft_state(buff_block)

                
                  

                
                    self.current_block = Block(self.chain.blocks[-1].index + 1, self.chain.blocks[-1].current_hash)

                    for _ in range(block_capacity):
                        if not self.pending_transactions:
                            break
                        trans = self.pending_transactions.popleft()
                        await self.add_transaction_to_block(trans)



                
                    
                    return {'status':200,'message':'Block added to chain', 'pk':self.wallet.public_key ,'new_balance':self.wallet.balance , 'new_stake':self.stake_amount}



                else:
                    if block.previous_hash != self.chain.blocks[-1].current_hash:
                        print(f"#########BLOCK INVALID - HASH MISMATCH ###########")

                    
                    elif block.validator != (validator['pk']):
                        print(f"#########BLOCK INVALID VALIDATOR PROBLEM INDEX {block.index} ###########")
                        print(f"Expected validator: {validator['pk']} but got {block.validator} ########")
                
                    return {'status':400,'message':'Block Invalid'}

