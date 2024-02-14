from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
import json

class Transaction:
    def __init__(self, sender_address, receiver_address, type_of_transaction, amount, nonce, message=None):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        if type_of_transaction not in ['coin', 'message']:
            raise ValueError("Value can only be 'coin' or 'message'")
        self.type_of_transaction = type_of_transaction
        self.amount = amount
        self.nonce = nonce
        self.message = message
        self.transaction_id = self.hash_transaction()
        self.signature = None

    def sign_transaction(self, private_key):
        """
        Sign the transaction with the sender's private key.
        """
        signer = pkcs1_15.new(private_key)
        h = SHA256.new(self.transaction_id.encode())
        self.signature = base64.b64encode(signer.sign(h)).decode() #TODO: may not need base64 encoding

    def verify_signature(self):
        """
        Verify the signature of the transaction.
        """
        public_key = RSA.import_key(self.sender_address)
        verifier = pkcs1_15.new(public_key)
        h = SHA256.new(self.transaction_id.encode())
        try:
            verifier.verify(h, base64.b64decode(self.signature.encode()))
            return True
        except (ValueError, TypeError):
            return False

    def hash_transaction(self):
        """
        Hashes the transaction details to generate a unique transaction ID.
        """
        transaction_details = {
            'sender_address': self.sender_address,
            'recipient_address': self.recipient_address,
            'type_of_transaction': self.type_of_transaction,
            'amount': self.amount,
            'nonce': self.nonce,
            'message': self.message
        }
        transaction_string = json.dumps(transaction_details, sort_keys=True)
        h = SHA256.new(transaction_string.encode())
        return h.hexdigest()
    
    
    def validate_transaction(self, wallet):
        """
        Validate the transaction.
        """
        if not self.verify_signature():
            return False
        if self.type_of_transaction == 'coin':
            senderBalance = wallet.get_balance(self.sender_address)
            if senderBalance < self.amount:
                return False
        else:
            senderBalance = wallet.get_balance(self.sender_address)
            message_size = len(self.message)
            if senderBalance < message_size:
                return False
        return True
        