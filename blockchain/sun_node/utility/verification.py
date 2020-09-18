""" Provides verification helper methods. """

from utility.hash_util import hash_block_256
from utility.constants import SUN
from wallet import Wallet


class Verification:
    """ Static and Class methods for verifying the security of the blockchain. """

    @staticmethod
    def verify_block_hash(block, given_hash):
        """ Checks if hashes match. """
        if given_hash == hash_block_256(block):
            return True
        return False

    @staticmethod
    def verify_block_signature(block):
        """ Verifies if the block is mined by the right person. """
        return Wallet.verify_block(block)

    @staticmethod
    def verify_block_proof(block, transactions):
        """ Verifies the proof and node_id (public key) of the current block. """
        sun_transactions = {}
        for tx in transactions:
            if tx.sender != SUN.PUBLIC_KEY:
                continue
            if tx.recipient not in sun_transactions:
                sun_transactions[tx.recipient] = tx.amount
            else:
                sun_transactions[tx.recipient] += tx.amount
        node_id = SUN.PUBLIC_KEY
        proof = 0
        for key, value in sun_transactions.items():
            if value > proof:
                node_id = key
                proof = value
        if node_id == SUN.PUBLIC_KEY:
            proof = sum(
                tx.amount for tx in transactions if tx.recipient == SUN.PUBLIC_KEY)
        proof = round(proof)
        if node_id == block.node_id and proof == block.proof:
            return True
        return False

    @classmethod
    def verify_chain(cls, chain):
        """ Verifies the current blockchain. """
        for (index, block) in enumerate(chain):
            if index == 0:
                continue
            if not cls.verify_block_proof(block, block.transactions):
                return False
            if not cls.verify_block_signature(block):
                return False
            if not cls.verify_block_hash(chain[index-1], block.previous_hash):
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        """ Verify a transaction checking if the sender has funds or just by checking the signature. """
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return (sender_balance >= transaction.amount and Wallet.verify_transaction(transaction))
        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, transactions, get_balance):
        """ Verifies all open transactions. """
        return all([cls.verify_transaction(tx, get_balance, False) for tx in transactions])
