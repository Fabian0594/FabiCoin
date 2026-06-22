from dataclasses import dataclass
from typing import List

from domain.transaction import Transaction


@dataclass
class Block:
    """Represents a block in the blockchain.

    This class serves as a domain model containing block data and the
    mining logic.
    """

    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int
    hash: str

    @staticmethod
    def calculate_hash(
        index: int,
        timestamp: float,
        transactions: List[Transaction],
        previous_hash: str,
        nonce: int,
    ) -> str:
        """Calculates the SHA-256 hash of a block's attributes."""
        import hashlib
        import json

        # Convert transactions to dicts for deterministic JSON dumping
        txs_list = [tx.__dict__ for tx in transactions]
        transactions_str = json.dumps(txs_list, sort_keys=True)

        block_string = f"{index}:{timestamp}:{transactions_str}:{previous_hash}:{nonce}"
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def mine(self, difficulty: int) -> None:
        """Mines the block by incrementing nonce until difficulty is met."""
        target = "0" * difficulty
        current_hash = self.calculate_hash(
            self.index,
            self.timestamp,
            self.transactions,
            self.previous_hash,
            self.nonce,
        )

        while not current_hash.startswith(target):
            self.nonce += 1
            current_hash = self.calculate_hash(
                self.index,
                self.timestamp,
                self.transactions,
                self.previous_hash,
                self.nonce,
            )

        self.hash = current_hash
