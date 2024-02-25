import time
import json
from Crypto.Hash import SHA256
from transaction import Transaction


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
        block.transactions = [data['transactions']]
        block.current_hash = data['hash']

        return block

    
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
