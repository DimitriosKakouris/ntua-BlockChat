from Crypto.PublicKey import RSA

class Wallet:
    def __init__(self):
        key = RSA.generate(2048)
        self.private_key = key.export_key().decode()
        self.public_key = key.publickey().export_key().decode()
        self.transactions = []
        self.nonce = 0
        self.balance = 1000
        
    def get_balance(self):
        return self.balance

def generate_wallet():
    return Wallet()