from dataclasses import dataclass
from typing import List

from domain.merkle_tree import build_merkle_root
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

        merkle_root = build_merkle_root(transactions)
        block_string = f"{index}:{timestamp}:{merkle_root}:{previous_hash}:{nonce}"
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

    @staticmethod
    def from_dict(data: dict) -> "Block":
        """Reconstructs a Block object from a dictionary representation."""
        transactions = [
            Transaction.from_dict(tx_data) for tx_data in data.get("transactions", [])
        ]
        return Block(
            index=data["index"],
            timestamp=data["timestamp"],
            transactions=transactions,
            previous_hash=data["previous_hash"],
            nonce=data["nonce"],
            hash=data["hash"],
        )
