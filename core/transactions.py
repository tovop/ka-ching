"""
Client class

Supplier and receiver of coins.
"""
import hashlib
import random
import string
import json
import binascii
import numpy as np
import pandas as pd
# import pylab as pl
import logging
import datetime
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from typing import Union


class Block(object):
    """
    Transaction block
    """

    def __init__(self):
        self.verified_transactions = list()
        self.previous_block_hash = None
        self.Nonce = None


class Client(object):
    """
    Provider and receiver of coins.
    """

    def __init__(self):
        random_generator_func = Crypto.Random.new().read
        self._private_key = RSA.generate(2048, random_generator_func)
        self._public_key = self._private_key.publickey()
        self._signer = PKCS1_v1_5.new(self._private_key)

    @property
    def identity(self):
        """The generated public key is used as the client's identity."""
        # create a HEX representation of the public key
        # this is unique to each client and can be made publicly available
        # this is used by other to send coins to you
        return binascii.hexlify(self._public_key.exportKey(format="DER")).decode("ascii")


class Transaction(object):
    """
    Coin transaction.
    """

    def __init__(self, sender: Union[Client, str], recipient: str, value: float):
        self.sender = sender
        self.recipient = recipient
        self.value = value
        tz = datetime.timezone(datetime.timedelta(hours=0))
        self.time = datetime.datetime.utcnow().replace(tzinfo=tz)   # timestamp in UTC (incl. time zone information)

    def to_dict(self):
        """Dictionary representation of the transaction."""
        if isinstance(self.sender, str):
            assert self.sender == "Genesis", "A transaction can only be initated from a Client unless it is the " \
                                             "Genesis block."
            identity = "Genesis"
        else:
            identity = self.sender.identity

        data = dict(
            sender=identity,
            recipient=self.recipient,
            value=self.value,
            time=self.time
        )
        return data

    def sign_transaction(self):
        """Sign the transaction using the senders private key."""
        signer = PKCS1_v1_5.new(self.sender._private_key)
        msg = SHA.new(str(self.to_dict()).encode("utf8"))
        return binascii.hexlify(signer.sign(msg)).decode("ascii")


def display_transactions(transactions: list):
    """Display transaction details."""
    msg = f"===============================================================\n"

    for transaction in transactions:
        data = transaction.to_dict()

        msg += f"---------------------------------------------------------------\n" \
               f"Sender   : {data.get('sender')}\n" \
               f"Receiver : {data.get('recipient')}\n" \
               f"Value    : {data.get('value')}\n" \
               f"Time     : {data.get('time')}\n"

    msg += f"===============================================================\n"

    print(msg)