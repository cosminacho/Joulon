import json
from block import Block
from transaction import Transaction
from wallet import Wallet

from utility.constants import SUN
from utility.verification import Verification
from utility.hash_util import hash_block_256


class Blockchain:
    """
    Attributes:
        :chain: Contains a list of all the blocks
        :transactions: A list containing all unmined transactions
        :node_id: The connected node which is hosting
        :public_key: The public key of the hosting node
        :peer_nodes: The nodes connected to the network
    """

    def __init__(self, node_id, public_key=None):
        """ The constructor of the blockchain. """
        genesis_block = Block(0, SUN.PUBLIC_KEY, 0, [], '', 0, "GENESIS")
        self.__chain = [genesis_block]
        self.__transactions = []
        self.__peer_nodes = set()
        self.node_id = node_id
        self.public_key = public_key
        if not self.load_data():
            self.save_data()

    def set_open_transactions(self, val):
        """ Sets the current open transactions list. """
        self.__transactions = val

    def get_open_transactions(self):
        """ Returns a copy of the open transactions list. """
        return self.__transactions[:]

    def set_chain(self, val):
        """ Replaces the current chain with val. """
        self.__chain = val

    def get_chain(self):
        """ Return a copy of the blockchain. """
        return self.__chain[:]

    def get_last_block(self):
        """ Get last chain block. """
        if len(self.__chain) == 0:
            return None
        return self.__chain[-1]

    def add_peer_node(self, node_id):
        """ Adds a new node to the peer node set. """
        self.__peer_nodes.add(node_id)

    def remove_peer_node(self, node_id):
        """ Remove a node from the set. """
        self.__peer_nodes.discard(node_id)

    def get_peer_nodes(self):
        """ Return a list of all connected nodes. """
        return list(self.__peer_nodes)

    def get_set_peer_nodes(self):
        """ Returns the set of the peer nodes. """
        return self.__peer_nodes

    def save_data(self):
        """ Saves the blockchain object to a local file. """
        try:
            with open("blockchain.txt", mode="w") as f:
                new_chain = []
                for block in self.__chain:
                    block.transactions = [
                        tx.__dict__ for tx in block.transactions]
                    new_chain.append(block.__dict__)
                f.write(json.dumps(new_chain))
                f.write("\n")
                saveable_transactions = [
                    tx.__dict__ for tx in self.__transactions]
                f.write(json.dumps(saveable_transactions))
                f.write("\n")
                return True
        except (IOError, IndexError):
            print("Savind data failed...")
            return False

    def load_data(self):
        """ Initialize the blockchain object with data from a file. """
        try:
            with open("blockchain.txt", mode="r") as f:
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    updated_block = Block.create_object(block)
                    updated_blockchain.append(updated_block)
                self.__chain = updated_blockchain

                transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in transactions:
                    updated_transaction = Transaction.create_object(tx)
                    updated_transactions.append(updated_transaction)
                self.__transactions = updated_transactions
                return True
        except (IOError, IndexError):
            print("Failed to load data from a file...")
            return False

    def proof_of_stake(self):
        """ Generate a (node_id, proof) tuple for the current block. """
        sun_transactions = {}
        for tx in self.__transactions:
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
                tx.amount for tx in self.__transactions if tx.recipient == SUN.PUBLIC_KEY)
        proof = round(proof)
        return (node_id, proof)

    def get_balance(self, wallet=None):
        """ Calculate and return the coin balance for a participant. """
        if wallet == None:
            if self.public_key == None:
                return None
            participant = self.public_key
        else:
            participant = wallet

        amount_recieved, amount_sent = 0, 0
        for block in self.__chain:
            for tx in block.transactions:
                if tx.recipient == participant:
                    amount_recieved += tx.amount
                elif tx.sender == participant:
                    amount_sent += tx.amount
                else:
                    continue
        return amount_recieved - amount_sent

    def add_transaction(self, transaction):
        """ Add a new transaction to the open_transactions. """
        if transaction.sender == SUN.PUBLIC_KEY:
            if Verification.verify_transaction(transaction, self.get_balance, False):
                self.__transactions.append(transaction)
                self.save_data()
                return True
            else:
                return False
        else:
            if Verification.verify_transaction(transaction, self.get_balance):
                self.__transactions.append(transaction)
                self.save_data()
                return True
            else:
                return False

    def add_block(self, block):
        """ Add a new block to the chain. """
        last_block = self.__chain[-1]
        if not Verification.verify_block_proof(block, self.__transactions):
            return False

        if not Verification.verify_block_hash(last_block, block.previous_hash):
            return False
        if not Verification.verify_block_signature(block):
            return False
        self.__chain.append(block)
        self.__transactions = []
        self.save_data()
        return True

    def mine_block(self):
        """ Create a new block and adds open transactions to it. """
        if self.public_key == None:
            return None
        last_block = self.__chain[-1]
        hashed_block = hash_block_256(last_block)
        node_id, proof = self.proof_of_stake()
        copied_transaction = self.__transactions[:]
        if not Verification.verify_transactions(copied_transaction, self.get_balance):
            return None
        block = Block(
            len(self.__chain),
            node_id,
            proof,
            copied_transaction,
            hashed_block)
        return block

    def resolve(self):
        """ Checks all peer nodes blockchains and replaces the local one with longer valid ones. """
        pass
        # Request all blocks from the nodes and check the longest valid chain
