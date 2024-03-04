from block import Block
import time
from wsmanager import send_websocket_request



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
        
        if node.current_block.validator != None:
            return {'minting_time': -1}
        
        # Implementing the proof of stake
        previous_block = self.blocks[-1]

        # Assuming each block has a 'current_hash' attribute
        # seed = int(previous_block.current_hash, 16)  # Convert hex hash to an integer
        
        # random.seed(seed)
       
        start_time = time.time()

        current_block = node.current_block

        curr_spending = {}
        for ring_member in node.ring:
            curr_spending[ring_member['public_key']] = 0

        curr_balances = {}
        for ring_member in node.ring:
            res = await send_websocket_request('get_balance', {},  ring_member['ip'], ring_member['port'])
            curr_balances[ring_member['public_key']] = res['balance']

        for transaction in current_block.transactions:
            flag = 1 if transaction.type_of_transaction == 'coin' else 0
            if int(curr_spending[transaction.sender_address]) + int(transaction.amount) * (1 + flag * 0.03)  > int(curr_balances[transaction.sender_address]):
                current_block.transactions.remove(transaction)
            else:
                curr_spending[transaction.sender_address] += int(transaction.amount) * (1 + flag * 0.03)

             

        if not node.validate_block(current_block):
            return {'minting_time': -1}
        
        current_block.validator = node.wallet.public_key
        # print(current_block.validator)

        # print(f'Node {node.id} is minting a block...')
    
       
        
        # Calculate minting time
        minting_time = time.time() - start_time

        await node.broadcast_block(current_block)

     
        return minting_time
    

