from blockchain import Blockchain
from wallet import Wallet


class Node:
    def __init__(self):
        self.chain = Blockchain()
        self.wallet = Wallet()
        self.ring = []
        self.id = None
        self.unconfirmed_transactions = []
        self.stake = 0

    def add_block(self, block):
        self.chain.add_block(block)
    
    def validate_block(self, block):
        return (block.previous_hash == self.chain.blocks[-1].current_hash) and (block.current_hash == block.hash_block())