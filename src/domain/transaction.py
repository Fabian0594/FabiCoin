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
    signature: str = ""

    @staticmethod
    def calculate_hash(
        sender: str, recipient: str, amount: float, timestamp: float
    ) -> str:
        """Calculates the SHA-256 hash of a transaction's attributes."""
        import hashlib

        transaction_string = f"{sender}:{recipient}:{amount}:{timestamp}"
        return hashlib.sha256(transaction_string.encode("utf-8")).hexdigest()

    def sign_transaction(self, signing_key: str) -> None:
        """Signs the transaction ID using the sender's private key (signing_key).

        Raises ValueError if the private key does not match the sender.
        """
        import ecdsa

        try:
            private_key_bytes = bytes.fromhex(signing_key)
            sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        except Exception as e:
            raise ValueError(f"Clave privada inválida: {e}") from e

        vk = sk.get_verifying_key()
        derived_public_key = vk.to_string().hex()

        if derived_public_key != self.sender:
            raise ValueError(
                "No se puede firmar: la clave privada no corresponde al emisor."
            )

        signature_bytes = sk.sign(self.id.encode("utf-8"))
        self.signature = signature_bytes.hex()

    def is_valid(self) -> bool:
        """Verifies if the transaction signature is cryptographically valid.

        Raises ValueError if the transaction is not signed.
        """
        if self.sender == "NETWORK":
            return True

        if not self.signature:
            raise ValueError("La transacción no está firmada.")

        import ecdsa

        try:
            vk = ecdsa.VerifyingKey.from_string(
                bytes.fromhex(self.sender), curve=ecdsa.SECP256k1
            )
            return vk.verify(bytes.fromhex(self.signature), self.id.encode("utf-8"))
        except (ecdsa.BadSignatureError, ValueError, TypeError):
            return False

    @staticmethod
    def from_dict(data: dict) -> "Transaction":
        """Reconstructs a Transaction object from a dictionary representation."""
        return Transaction(
            sender=data["sender"],
            recipient=data["recipient"],
            amount=data["amount"],
            timestamp=data["timestamp"],
            id=data["id"],
            signature=data.get("signature", ""),
        )
