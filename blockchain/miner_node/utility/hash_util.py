import hashlib
import json


def hash_string_256(string):
    """ Hashes a normal string with SHA256 algorithm. """
    return hashlib.sha256(string).hexdigest()


def hash_transaction_256(transaction):
    """ Hashes a transaction with the SHA256. """
    hashable_transaction = transaction.to_ordered_dict()
    return hash_string_256(json.dumps(hashable_transaction).encode())


def hash_block_256(block):
    """ Hashes a block with the SHA256. """
    hashable_block = block.to_ordered_dict()
    return hash_string_256(json.dumps(hashable_block).encode())
