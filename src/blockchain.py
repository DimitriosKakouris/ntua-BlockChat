from block import Block
import time
import asyncio


class Blockchain:
    def __init__(self):
        self.blocks = [] #block.genesis()
        self.blockchain_lock = asyncio.Lock()
    
        

    
    def to_dict(self):
        return {
            'blocks': [block.to_dict() for block in self.blocks]
        }
    
    
    def from_dict(self, data):
        for block_data in data['blocks']:
            block = Block.from_dict(block_data) 
            self.blocks.append(block)
        return self



    async def add_block(self, block, node):
        buff_blocks_added = []
        self.blocks.append(block)
        
        while len(self.blocks)+1 in node.block_buffer:
            next_block = node.block_buffer.pop(len(self.blocks)+1)
            print(f"Popping block {next_block.index}")
            if await node.validate_block(next_block):
                print(f"Adding block from buffer {next_block.index}")
                
                self.blocks.append(next_block)
                buff_blocks_added.append(next_block.to_dict())
            else:
                break

        return buff_blocks_added
    




    def size(self):
        return len(self.blocks)



    def mint_block(self, node):
       
            start_time = time.time()
            current_block = node.current_block
            current_block.validator = node.wallet.public_key
            # Calculate minting time
            minting_time = time.time() - start_time

        
            return minting_time
        

