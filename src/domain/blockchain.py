import time
from typing import List

from domain.block import Block
from domain.transaction import Transaction


class Blockchain:
    """Represents a blockchain that manages a chain of blocks.

    It automatically initializes with a Genesis block.
    """

    def __init__(self) -> None:
        self._chain: List[Block] = []
        self._create_genesis_block()

    @property
    def chain(self) -> List[Block]:
        """Returns the list of blocks in the chain."""
        return self._chain

    def _create_genesis_block(self) -> None:
        # Create genesis block with index 0 and previous_hash "0"
        timestamp = time.time()
        transactions: List[Transaction] = []
        previous_hash = "0"
        nonce = 0
        genesis_hash = Block.calculate_hash(
            index=0,
            timestamp=timestamp,
            transactions=transactions,
            previous_hash=previous_hash,
            nonce=nonce,
        )
        genesis_block = Block(
            index=0,
            timestamp=timestamp,
            transactions=transactions,
            previous_hash=previous_hash,
            nonce=nonce,
            hash=genesis_hash,
        )
        self._chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        """Returns the last block added to the chain."""
        return self._chain[-1]

    def add_block(self, new_block: Block) -> None:
        """Appends a new, pre-mined block to the chain.

        Raises:
            ValueError: If the block is invalid (hash or previous_hash is incorrect).
        """
        latest_block = self.get_latest_block()

        # Invariant 1: previous_hash must match the latest block's hash
        if new_block.previous_hash != latest_block.hash:
            raise ValueError("Bloque inválido: previous_hash incorrecto.")

        # Invariant 2: hash must match the recalculated hash of block state
        recalculated_hash = Block.calculate_hash(
            new_block.index,
            new_block.timestamp,
            new_block.transactions,
            new_block.previous_hash,
            new_block.nonce,
        )
        if new_block.hash != recalculated_hash:
            raise ValueError("Bloque inválido: hash incorrecto.")

        self._chain.append(new_block)

    def is_chain_valid(self) -> bool:
        """Validates the immutability and integrity of the blockchain."""
        if not self._chain:
            return False

        # Validate genesis block hash
        genesis = self._chain[0]
        recalculated_genesis_hash = Block.calculate_hash(
            genesis.index,
            genesis.timestamp,
            genesis.transactions,
            genesis.previous_hash,
            genesis.nonce,
        )
        if genesis.hash != recalculated_genesis_hash:
            return False

        # Validate subsequent blocks
        for i in range(1, len(self._chain)):
            current = self._chain[i]
            previous = self._chain[i - 1]

            # Invariant 1: Hash must match recalculated hash of attributes
            recalculated_hash = Block.calculate_hash(
                current.index,
                current.timestamp,
                current.transactions,
                current.previous_hash,
                current.nonce,
            )
            if current.hash != recalculated_hash:
                return False

            # Invariant 2: Current previous_hash must match previous block's hash
            if current.previous_hash != previous.hash:
                return False

        return True
