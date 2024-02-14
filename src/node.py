from blockchain import Blockchain
from transaction import Transaction
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
    
    def register_node_to_ring(self, id, ip, port, public_key, balance):
        self.ring.append({
            "id": id,
            "ip": ip,
            "port": port,
            "public_key": public_key,
            "balance": balance
        })

    def create_transaction(self, receiver, receiver_id, amount):
        """Creates a new transaction, adjusting the balances of the sender and receiver"""

        # Check if the sender has enough balance
        if self.wallet.balance < amount:
            return {"mining_time": 0, "success": False}

        # Create the transaction
        # Assuming a Transaction class exists that can handle account-based models
        transaction = Transaction(sender_address=self.id, receiver_address=receiver_id, amount=amount)

        # Deduct the amount from the sender's balance
        self.wallet.balance -= amount

        # In a real blockchain, the receiver's balance would be updated when the transaction is confirmed
        # However, for simplicity, this example assumes immediate balance update
        # Note: In a real application, updating the receiver's balance directly like this isn't secure
        # as it doesn't go through the blockchain validation process.
        # receiver.wallet.balance += amount (This should be handled by the transaction processing mechanism)

        # Add the transaction to a list of pending transactions, for example
        self.pending_transactions.append(transaction)

        return {"mining_time": X, "success": True}  # Replace X with the actual time it takes to mine the transaction, if applicable
