import ecdsa


class Wallet:
    """Represents a cryptocurrency wallet.

    Generates and holds a SECP256k1 private and public key pair in
    hexadecimal format. The public key serves as the user's public address.
    """

    def __init__(self) -> None:
        private_key_obj = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key_obj = private_key_obj.get_verifying_key()

        self.private_key = private_key_obj.to_string().hex()
        self.public_key = public_key_obj.to_string().hex()
