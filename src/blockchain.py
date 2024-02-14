from block import Block
import random
from datetime import datetime
import time

class Blockchain:
    def __init__(self):
        block = Block()
        self.blocks = [block.genesis()]

    def add_block(self, block):
        self.blocks.append(block)

    def mint_block(self, node, capacity):
        if len(self.current_transactions) >= capacity: 
            # Implementing the proof of stake
            seed = sum(ord(c) for c in str(datetime.now()))  # Simple seed based on current time
            random.seed(seed)
            validator = self.select_validator()

            start_time = time.time()
            # Assuming 'select_validator' randomly selects based on stake
            if validator.id == node.id:  # Assuming you have a way to identify the current node
                previous_hash = self.chain.blocks[-1].current_hash if self.chain else '1'
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
