import time
import Crypto
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


    def genesis(self, n):
        genesis_block = Block(0, 1)
        genesis_transaction = Transaction('0', self.wallet.public_key, 'coin', 1000*n, 0) #TODO: may want to change the sender and recepient address
        genesis_block.transactions.append(genesis_transaction)

    def add_transaction(self, transaction, capacity):
        self.transactions.append(transaction)
        if len(self.transactions) >= capacity:
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
    
    
