from block import Block
import random
from datetime import datetime
import time

class Blockchain:
    def __init__(self):
        #block = Block()
        self.blocks = [] #block.genesis()

    
    def to_dict(self):
        return {
            'blocks': [block.to_dict() for block in self.blocks]
        }
    
    
    def from_dict(self, data):
        for block_data in data['blocks']:
            block = Block.from_dict(block_data)  # Assuming Block has a similar from_dict method
            self.add_block(block)
        return self

    def add_block(self, block):
        self.blocks.append(block)

    def size(self):
        return len(self.blocks)

    def mint_block(self, node, capacity):
        if len(self.current_transactions) >= capacity: 
            # Implementing the proof of stake

            # Use the hash of the previous block as the seed for the pseudorandom number generator
            if self.blocks:  # Ensure there is at least one block in the chain
                previous_block = self.blocks[-1]
                # Assuming each block has a 'current_hash' attribute
                seed = int(previous_block.current_hash, 16)  # Convert hex hash to an integer
            else:
                # Fallback seed for the very first block (genesis block)
                seed = 1
            random.seed(seed)
            validator = self.select_validator(node.ring)

            start_time = time.time()
            
            if validator.id == node.id:  # Assuming you have a way to identify the current node
                previous_hash = self.blocks[-1].current_hash if self.blocks else '1'
                new_block = Block(
                    transactions=node.unconfirmed_transactions,
                    previous_hash=previous_hash,
                    validator_address=validator
                )
                self.add_block(new_block)
                # Calculate minting time
                minting_time = time.time() - start_time
                return minting_time
            else:
                return 0
        else:
            return 0

    def select_validator(nodes):
        """
        Selects a validator node based on the stake of each node.
        The higher the stake, the higher the chance of being selected as a validator.
        
        :param nodes: A list of Node objects, where each node has an 'id' and 'stake'.
        :return: The selected Node object as the validator.
        """
        total_stake = sum(node.stake for node in nodes)
        selection_point = random.uniform(0, total_stake)
        current = 0
        for node in nodes:
            current += node.stake
            if current >= selection_point:
                return node

        # Fallback, should not reach here if implemented correctly
        raise Exception("Failed to select a validator. Check the implementation.")
