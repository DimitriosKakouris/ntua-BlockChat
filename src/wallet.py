from Crypto.PublicKey import RSA

class Wallet:
    def __init__(self):
        key = RSA.generate(2048)
        self.private_key = key.export_key().decode()
        self.public_key = key.publickey().export_key().decode()
        # self.transactions = []
        self.nonce = 0
        self.balance = 0
        
    def get_balance(self):
        return self.balance

def generate_wallet():
    return Wallet()


# ETHEREUM WALLET TYPE


# import ecdsa

# class Wallet:
#     def __init__(self):
#         key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)  # SECP256k1 is the curve used by Bitcoin
#         self.private_key = key.to_string().hex()  # Convert to hexadecimal for easier storage and readability
#         self.public_key = key.get_verifying_key().to_string().hex()
#         self.transactions = []
#         self.nonce = 0
#         self.balance = 0

#     def get_balance(self):
#         return self.balance

# def generate_wallet():
#     return Wallet()