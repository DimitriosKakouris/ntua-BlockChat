from blockchain import Blockchain
from transaction import Transaction
from wallet import Wallet
from block import Block
from wsmanager import send_websocket_request
import asyncio
import random


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

       

   
    # def update_balance(self, public_key, balance):
    #     if public_key not in self.account_space:
    #         self.account_space[public_key] = {'balance': balance}
    #     else:
    #         self.account_space[public_key]['balance'] = balance
    

    

    # def get_balance(self, public_key):
    #     if public_key in self.account_space:
    #         return self.account_space[public_key]['balance']
    #     else:
    #         return None
        

    async def stake(self, amount):
        """
        Updates the node's stake amount for the Proof of Stake process.
        The node can increase or decrease its stake, within the limits of its available balance.
        """
        return await self.create_transaction('0', "coin", amount)

        # if not stake_trasaction["success"]:
        #     return False
        
        # else:
        #     #self.stake = amount
        #     return True
    

    async def validate_transaction(self,transaction):
        """
        Validate the transaction.
        """
        print("I am in 'validate_transaction'")
        if not transaction.verify_signature():
            return False
        
    
        sender_balance = self.account_space[transaction.sender_address]['balance']

        flag = 1 if transaction.type_of_transaction == 'coin' and (self.account_space[transaction.sender_address]['id']!= 0 or transaction.nonce >= len(self.ring) ) else 0
        stake_flag = 1 if transaction.receiver_address == '0' else 0
        if int(transaction.amount) * (1 + flag * 0.03)  > int(sender_balance) + int(self.account_space[transaction.sender_address]['stake']) * stake_flag:
            return False
        # print('Transaction:', transaction.to_dict())
        # print('Balance:', int(sender_balance))
        # print('Transaction amount+fees:', int(transaction.amount) * (1 + flag * 0.03))
     
        return True
        
    async def validate_block(self, block):
        # seed = int(self.previous_hash, 16)  # Convert hex hash to an integer
        # random.seed(seed)
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
                "balance": 3000,
                "valid_balance":3000,
                "stake": 0,
                "valid_stake": 0
            }
        else:
            self.account_space[public_key] = {
                'id' : id,
                "ip": ip,
                "port": port,
                "balance": 1000,
                "stake": 0,
            }

    
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
        res = await self.broadcast_transaction(transaction)
        

        if res['valid']:
            self.wallet.nonce += 1
            return True

           
        
        else:
            print("Invalid transaction")
            return False
             
            

    async def send_initial_bcc(self):
        for ring_node in self.ring:
            if ring_node['id'] != 0:
                # print("Sending coins to node", ring_node['id'])

                if await self.create_transaction(ring_node['public_key'],'coin',1000):
                    print(f"Node {ring_node['id']} successfully received 1000 BCCs")


                        #await websocket.send(json.dumps({'message' :f"Node {node.id} successfully received 1000 BCCs"}))
    
    
       
    

    # async def trigger_fees(self, fees_sum):
    #     for ring_node in self.ring:
    #             if ring_node['public_key'] == validator:
    #                 await send_websocket_request('get_fees', {'fees':fees_sum},  ring_node['ip'], ring_node['port'])
    #                 break



    async def update_balance(self):
        transaction_pool_copy = self.transaction_pool.copy()
        fees_sum = 0
        for trans in transaction_pool_copy:
            if any(trans.transaction_id == transaction.transaction_id for transaction in self.chain.blocks[-1].transactions):
                flag = 1 if trans.type_of_transaction == 'coin' and (self.account_space[trans.sender_address]['id']!= 0 or trans.nonce >= len(self.ring)) else 0 #bootstrap node isn't charged a fee when executing the genesis transactions
                if trans.sender_address == self.wallet.public_key and trans.receiver_address != '0': #regural transaction
                    self.wallet.balance -= int(trans.to_dict()['amount']) * (1 + flag * 0.03)
                    fees_sum += flag * 0.03 * int(trans.to_dict()['amount'])
                
                elif trans.sender_address == self.wallet.public_key and trans.receiver_address == '0': #transaction is stake(amount)
                    self.wallet.balance += self.stake_amount
                    self.stake_amount = int(trans.to_dict()['amount'])
                    self.wallet.balance -= self.stake_amount

                if trans.receiver_address == self.wallet.public_key:
                    if trans.type_of_transaction == 'message': #message 
                        fees_sum += int(trans.to_dict()['amount'])
                    else: #regular transaction
                        self.wallet.balance += int(trans.to_dict()['amount'])
                    
                # Remove the transaction from the original transaction_pool
                self.transaction_pool.remove(trans)

        return fees_sum
    

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
        response = await send_websocket_request('update_block', transaction.to_dict(),  node['ip'], node['port'])
        
        return response

    async def broadcast_transaction(self, transaction):
        """Broadcasts a transaction to the network using WebSockets."""
        tasks = []
        responses = []

        tasks = [self.send_transaction(node, transaction) for node in self.ring]

        responses = await asyncio.gather(*tasks)

        if any(res["message"] == "Transaction Invalid" for res in responses):
            
            return {'valid': False}
        
        elif any(res["message"] == "Transaction added to block" for res in responses):
            return {'valid': True,'full': False}
        
        elif any(res["message"] == "Block is full" for res in responses):
            return {'valid': True,'full': True}
        
       



       

        # print("Responses:", responses)

     
        # await send_websocket_request('update_balance', {},  self.ip, self.port)
        # # Check responses for validation and receipt acknowledgment
      

    async def send_block(self, node, block):
        res = await send_websocket_request('new_block', block.to_dict(),  node['ip'], node['port'])
        return res
    

    async def broadcast_block(self, block):
        """Broadcasts a block to the network using WebSockets."""
        tasks = []
        responses = []


        tasks = [self.send_block(node, block) for node in self.ring if node['id']]

        

        responses = await asyncio.gather(*tasks)
        print("Responses:", responses)

        for res in responses:
            if res['status'] == 200:
               self.wallet.balance += res['fees']
            else:
                print("Block rejected by the network")
                break

        if await self.validate_block(block):
            self.chain.add_block(block)
            fees_sum = await self.update_balance()

            self.wallet.balance += fees_sum 

         
            for ring_node in self.ring:
                balance = 100
                self.account_space[ring_node['public_key']]['balance'] = balance['balance']
                self.account_space[ring_node['public_key']]['stake'] = balance['stake']

            
            for ring_node in self.ring:
                if ring_node['id'] != self.id:
                    await send_websocket_request('update_soft_state', self.account_space, ring_node['ip'], ring_node['port'])


      
               



        # for response in responses:
        #     if response['status'] == 200:
               
        #     #    print("Block accepted by the network")
        #        for ring_node in self.ring:
        #             await send_websocket_request('update_balance', {},  ring_node['ip'], ring_node['port'])
                    
        #        break
            
        #     else:
        #         # print("Block rejected by the network")
        #         break
                    

   
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

    async def mint_block(self):
        validator = await self.current_block.select_validator(self)

        await self.chain.mint_block(self)

        if self.id == validator['id']:

            await self.broadcast_block(self.current_block)
    
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
                            


   
