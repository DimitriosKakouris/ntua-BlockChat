import random
import time
import json
from Crypto.Hash import SHA256
from transaction import Transaction
import websockets


class Block:
    def __init__(self, index, previous_hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.transactions = []
        self.current_hash = self.hash_block()
        self.validator = None
        self.capacity = 2


    def add_transaction(self, transaction):
       
        print(f"Adding transaction to block {transaction.to_dict()}")
        print(f"Current transactions array is {self.transactions}")
        self.transactions.append(transaction)
        print(f"Transaction added to block and curr length is {len(self.transactions)}")
        if len(self.transactions) >= self.capacity:
            print(f"Block is full")
            return True # Block is full
        return False
    
    def hash_block(self):
        block_json = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "transactions": self.transactions #TODO: it may want ids instead of transactions
        }
        block_json = json.dumps(block_json, sort_keys=True)
        return SHA256.new(block_json.encode()).hexdigest()
    
    def view_block(self):
        validator = self.validator
        list_of_transactions = [transaction.to_dict() for transaction in self.transactions]
        block_json ={
            "validator": validator,
            "transactions": list_of_transactions
        }
        return block_json
    
    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [transaction.to_dict() for transaction in self.transactions],  # Assuming Transaction has a to_dict method
            'previous_hash': self.previous_hash,
            'hash': self.current_hash,
        }
    
    @classmethod
    def from_dict(cls, data):
        block = cls(data['index'], data['previous_hash'])
        block.timestamp = data['timestamp']
        block.transactions = [Transaction.from_dict(t) for t in data['transactions']]
        block.current_hash = data['hash']

        return block

    

    async def select_validator(self,nodes):
        """
        Selects a validator node based on the stake of each node.
        The higher the stake, the higher the chance of being selected as a validator.
        
        :param nodes: A list of Node objects, where each node has an 'id' and 'stake'.
        :return: The selected Node object as the validator.
        """

        total_stake = []
        for ring_node in nodes:
            res = await send_websocket_request('get_stake', {}, ring_node['ip'], ring_node['port'])
            res_data = {'stake': res['stake'], 'ip': ring_node['ip'], 'port': ring_node['port'], 'id': ring_node['id']}
            total_stake.append(res_data) # Has stake, ip, port, id

        print(total_stake[0]['stake'])
       
        
        total_stake_sum = 0
        for res in total_stake:
            total_stake_sum += int(res['stake'])

        # total_stake = sum(node.stake for node in nodes)
        selection_point = random.uniform(0, total_stake_sum)

        current = 0
        for res in total_stake:
            current += int(res['stake'])
            if current >= selection_point:
                return res # Return the selected node's ip, port, id

        # Fallback, should not reach here if implemented correctly
        raise Exception("Failed to select a validator. Check the implementation.")

# async def genesis(bootstrap_node_address, n):
#     genesis_block = Block(0, 1)
#     genesis_block.validator = 0
#     genesis_transaction = Transaction(
#         sender_address='0', 
#         receiver_address=bootstrap_node_address, 
#         type_of_transaction='coin', 
#         amount=1000*n, 
#         nonce=0) 
    

    
#     genesis_block.transactions.append(genesis_transaction)
#     return genesis_block

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
              