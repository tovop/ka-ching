"""
The core
"""
import json
from hashlib import sha256
from .utils import utc_now


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = None

    def compute_hash(self):
        """Compute the block hash."""
        block_string = json.dumps(
            dict(
                index=self.index,
                transactions=self.transactions,
                timestamp=self.timestamp.timestamp,
                previoush_hash=self.previous_hash,
                nonce=self.nonce
            )
        )
        return sha256(block_string.encode("utf-8")).hexdigest()


class Blockchain:
    def __init__(self, difficulty=2):
        self.difficulty = difficulty
        self.unconfirmed_transactions = list()
        self.blocks = list()
        self.create_genesis_block()

    def add_block(self, block, proof):
        """Add new block to the chain."""
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            # the new block is not referring to the currently last block in the chain
            return False

        if not self.is_valid_proof(block, proof):
            # the proof of work is invalid
            return False

        block.hash = proof
        self.blocks.append(block)
        return True

    def add_new_transaction(self, transaction):
        """Add a new transaction to the transaction queue."""
        self.unconfirmed_transactions.append(transaction)

    def create_genesis_block(self):
        """Create the first block aka. Genesis block."""
        genesis_block = Block(0, [], utc_now(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.blocks.append(genesis_block)

    def chain_size(self):
        """Size/length of block chain including the Genesis block."""
        return len(self.blocks)

    def is_valid_proof(self, block, block_hash):
        """Validate the proof of work."""
        return block_hash.startswith(self.prefix) and block_hash == block.compute_hash()

    @property
    def last_block(self):
        """Return the last block in the chain."""
        return self.blocks[-1]

    def mine(self):
        """
        Mine a new block.

        Compute proof of work and add transactions block to chain.
        """
        if len(self.unconfirmed_transactions) < 1:
            return None

        last_block = self.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            timestamp=utc_now(),
            previous_hash=last_block.hash
        )

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = list()
        return new_block.index

    @property
    def prefix(self):
        """Hash prefix."""
        return "0" * self.difficulty

    def proof_of_work(self, block):
        """
        Compute the block hash using a proof-of-work system.

        The proof-of-work system makes it progressively more difficult to perform the work required to create a new
        block. This means that someone who modifies a previous block would have to redo the work of the block and all
        of the blocks that follow it. The proof-of-work system requires scanning for a value that starts with a certain
        number of zero bits when hashed. This value is known as a nonce value. The number of leading zero bits is known
        as the difficulty. The average work required to create a block increases exponentially with the number of
        leading zero bits, and therefore, by increasing the difficulty with each new block, we can sufficiently prevent
        users from modifying previous blocks, since it is practically impossible to redo the following blocks and catch
        up to others.
        """
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith(self.prefix):
            # increment block nonce until hash satisfies the required difficulty
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def verify(self):
        """
        Verify that the block chain is not tampered with.

        Data integrity is important to databases, and blockchains provide an easy way to verify all the data:

        - Index in blocks[i] is i, and hence no missing or extra blocks.
        - Compute block hash H(blocks[i]) and cross-check with the recorded hash. Even if a single bit in a block is
          altered, the computed block hash would be entirely different.
        - Verify if H(blocks[i]) is correctly stored in next block’s previous_hash.
        - Check if there is any backdating by looking into the timestamps.
        """
        ok = True
        details = list()
        for i in range(1, self.chain_size()):
            if self.blocks[i].index != i:
                ok = False
                details.append(f"Wrong block index at block {i}")

            if self.blocks[i - 1].hash != self.blocks[i].previous_hash:
                ok = False
                details.append(f"Wrong previous hash at block {i}")

            if self.blocks[i].hash != self.blocks[i].compute_hash():
                ok = False
                details.append(f"Wrong hash at block {i}")

            if self.blocks[i - 1].timestamp >= self.blocks[i].timestamp:
                ok = False
                details.append(f"Backdating at block {i}")

        return ok, details
