from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import Crypto.Random
import binascii
import json


class Wallet:
    """ Creates, loads and holds private and public keys. Manages transaction signing and verification. """

    def __init__(self, node_id, private_key=None, public_key=None):
        """ node_id is the id generated from uuid. """
        self.__private_key = private_key
        self.public_key = public_key
        self.node_id = node_id

    def create_keys(self):
        """ Create a new pair of private and public keys. """
        private_key, public_key = Wallet.generate_keys()
        self.__private_key = private_key
        self.public_key = public_key

    def get_keys(self):
        """ Returns a tuple of the keys. """
        return (self.__private_key, self.public_key)

    @staticmethod
    def generate_keys():
        """ Generate a new pair of private and public key. """
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (
            binascii.hexlify(private_key.exportKey(
                format="DER")).decode('ascii'),
            binascii.hexlify(public_key.exportKey(
                format="DER")).decode('ascii')
        )

    def save_keys(self):
        """ Saves the keys to a file (wallet.txt). """
        if self.public_key is not None and self.__private_key is not None:
            try:
                with open(f"wallet-{self.node_id}.txt", mode="w") as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.__private_key)

            except (IOError, IndexError):
                print("Saving wallet failed...")

        return True

    def load_keys(self):
        """ Loads the keys from the wallet.txt file into memory. """
        try:
            with open(f"wallet-{self.node_id}.txt", mode="r") as f:
                keys = f.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key = public_key
                self.__private_key = private_key
        except (IOError, IndexError):
            print("Loading wallet failed...")
        return True

    def sign_transaction(self, transaction):
        """ Sign a transaction and return the signature. """
        signer = PKCS1_v1_5.new(RSA.importKey(
            binascii.unhexlify(self.__private_key)))
        hashable_transaction = transaction.to_ordered_dict()
        h = SHA256.new(json.dumps(hashable_transaction).encode())
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    def sign_block(self, block):
        """ Sign a block and return the signature. """
        signer = PKCS1_v1_5.new(RSA.importKey(
            binascii.unhexlify(self.__private_key)))
        hashable_block = block.to_ordered_dict()
        h = SHA256.new(json.dumps(hashable_block).encode())
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        """ Verify the signature of a transaction. """
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        hashable_transaction = transaction.to_ordered_dict()
        h = SHA256.new(json.dumps(hashable_transaction).encode())
        return verifier.verify(h, binascii.unhexlify(transaction.signature))

    @staticmethod
    def verify_block(block):
        """ Verify the signature of a block. """
        public_key = RSA.importKey(binascii.unhexlify(block.node_id))
        verifier = PKCS1_v1_5.new(public_key)
        hashable_block = block.to_ordered_dict()
        h = SHA256.new(json.dumps(hashable_block).encode())
        return verifier.verify(h, binascii.unhexlify(block.signature))
