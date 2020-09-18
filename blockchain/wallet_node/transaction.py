from time import time
from utility.printable import Printable
from collections import OrderedDict


class Transaction(Printable):
    """
    Attributes:
        :sender: The sender of the coins. (ID - public_key)
        :recipient: The recipient of the coins. (ID - public_key)
        :amount: The amount of coins sent.
        :description: A summary of the purpose of the transaction.
        :timestamp: The time when the transaction was made.
        :signature: The signature of the transaction.
    """

    def __init__(self, sender, recipient, amount, description="MINING", time=time(), signature=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.description = description
        self.timestamp = time
        self.signature = signature

    def to_ordered_dict(self):
        return OrderedDict([
            ('sender', self.sender),
            ('recipient', self.recipient),
            ('amount', self.amount),
            ('description', self.description),
            ('timestamp', self.timestamp)
        ])

    def add_signature(self, signature):
        self.signature = signature

    @staticmethod
    def create_object(dict_transaction):
        transaction = Transaction(
            dict_transaction["sender"],
            dict_transaction["recipient"],
            dict_transaction["amount"],
            dict_transaction["description"],
            dict_transaction["timestamp"],
            dict_transaction["signature"])
        return transaction
