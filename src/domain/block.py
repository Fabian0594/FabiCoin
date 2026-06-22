from dataclasses import dataclass
from typing import Any


@dataclass
class Block:
    """Represents a block in the blockchain.

    This class serves as a domain model containing block data and the
    mining logic.
    """

    index: int
    timestamp: float
    data: Any
    previous_hash: str
    nonce: int
    hash: str

    @staticmethod
    def calculate_hash(
        index: int, timestamp: float, data: Any, previous_hash: str, nonce: int
    ) -> str:
        """Calculates the SHA-256 hash of a block's attributes."""
        import hashlib
        import json

        # Serializar la data de manera determinista si es un dict/list
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)

        block_string = f"{index}:{timestamp}:{data_str}:{previous_hash}:{nonce}"
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def mine(self, difficulty: int) -> None:
        """Mines the block by incrementing nonce until difficulty is met."""
        target = "0" * difficulty
        current_hash = self.calculate_hash(
            self.index, self.timestamp, self.data, self.previous_hash, self.nonce
        )

        while not current_hash.startswith(target):
            self.nonce += 1
            current_hash = self.calculate_hash(
                self.index, self.timestamp, self.data, self.previous_hash, self.nonce
            )

        self.hash = current_hash
