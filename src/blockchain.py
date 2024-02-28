from block import Block
import random
import json
import websockets
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

    async def mint_block(self, node):
        
        # Implementing the proof of stake
        previous_block = self.blocks[-1]

        # Assuming each block has a 'current_hash' attribute
        seed = int(previous_block.current_hash, 16)  # Convert hex hash to an integer
        
        random.seed(seed)
       
        start_time = time.time()

        current_block = node.current_block
        
        current_block.validator = node.wallet.public_key

        print(f'Node {node.id} is minting a block...')
        

        # new_block = Block(
        #     index=self.blocks[-1].index + 1 ,
        #     previous_hash=self.blocks[-1].current_hash,
        # )
       

       
        
        # Calculate minting time
        minting_time = time.time() - start_time

        await node.broadcast_block(current_block)

     
        return minting_time
    


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
              