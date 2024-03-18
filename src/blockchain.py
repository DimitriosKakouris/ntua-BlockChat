from block import Block
import time
import asyncio


class Blockchain:
    def __init__(self):
        #block = Block()
        self.blocks = [] #block.genesis()
        # self.blockchain_lock = asyncio.Lock()
        

    
    def to_dict(self):
        return {
            'blocks': [block.to_dict() for block in self.blocks]
        }
    
    
    def from_dict(self, data):
        for block_data in data['blocks']:
            block = Block.from_dict(block_data)  # Assuming Block has a similar from_dict method
            self.blocks.append(block)
        return self

    def add_block(self, block):
     
            self.blocks.append(block)

    def size(self):
        return len(self.blocks)

    def mint_block(self, node):
       
            start_time = time.time()
            current_block = node.current_block
        

            current_block.validator = node.wallet.public_key

        
            
            # Calculate minting time
            minting_time = time.time() - start_time

        
            return minting_time
        

