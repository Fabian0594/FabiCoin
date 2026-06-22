from dataclasses import dataclass


@dataclass
class Transaction:
    """Represents a transaction of value in the blockchain.

    This class serves as a domain model containing transaction details.
    """

    sender: str
    recipient: str
    amount: float
    timestamp: float
    id: str

    @staticmethod
    def calculate_hash(
        sender: str, recipient: str, amount: float, timestamp: float
    ) -> str:
        """Calculates the SHA-256 hash of a transaction's attributes."""
        import hashlib

        transaction_string = f"{sender}:{recipient}:{amount}:{timestamp}"
        return hashlib.sha256(transaction_string.encode("utf-8")).hexdigest()
