import random
import time
import json
from Crypto.Hash import SHA256
from transaction import Transaction
from wsmanager import send_websocket_request
import os
from dotenv import load_dotenv
load_dotenv()
block_capacity = int(os.getenv('BLOCK_CAPACITY', 5))

class Block:
    def __init__(self, index, previous_hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.transactions = []
        self.current_hash = self.hash_block()
        self.validator = None
        self.capacity = block_capacity


    def add_transaction(self, transaction):
       
        # print(f"Adding transaction to block {transaction.to_dict()}")
        # print(f"Current transactions array is {self.transactions}")
        print("I am in 'add_transaction'")
        self.transactions.append(transaction)
        # print(f"Transaction added to block and curr length is {len(self.transactions)}")
        if len(self.transactions) >= self.capacity:
            # print(f"Block is full")
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
            'validator': self.validator
        }
    
    @classmethod
    def from_dict(cls, data):
        block = cls(data['index'], data['previous_hash'])
        block.timestamp = data['timestamp']
        block.transactions = [Transaction.from_dict(t) for t in data['transactions']]
        block.current_hash = data['hash']
        block.validator = data['validator']
        block.capacity = block_capacity

        return block

    

    async def select_validator(self,node):
        """
        Selects a validator node based on the stake of each node.
        The higher the stake, the higher the chance of being selected as a validator.
        
        :param nodes: A list of Node objects, where each node has an 'id' and 'stake'.
        :return: The selected Node object as the validator.
        """

        total_stake = []
        for pk in node.account_space:

            node_stake = node.account_space[pk]
            node_stake['pk'] = pk
            total_stake.append(node_stake) # Has stake, ip, port, id

        # print(total_stake[0]['stake'])
       
        
        total_stake_sum = 0
        for node_stake in total_stake:
            total_stake_sum += int(node_stake['stake'])

        seed = int(self.previous_hash, 16)  # Convert hex hash to an integer
        
        random.seed(seed)

        # total_stake = sum(node.stake for node in nodes)
        selection_point = random.uniform(0, total_stake_sum)

        current = 0
        for node_stake in total_stake:
            current += int(node_stake['stake'])
            if current >= selection_point:
              
                return node_stake 

        # Fallback, should not reach here if implemented correctly
        raise Exception("Failed to select a validator. Check the implementation.")

