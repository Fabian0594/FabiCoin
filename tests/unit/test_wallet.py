from domain.wallet import Wallet


def test_wallet_key_generation() -> None:
    wallet = Wallet()

    assert hasattr(wallet, "private_key")
    assert hasattr(wallet, "public_key")
    assert isinstance(wallet.private_key, str)
    assert isinstance(wallet.public_key, str)

    # SECP256k1 private key is 32 bytes (64 hex characters)
    assert len(wallet.private_key) == 64
    # SECP256k1 public key is 64 bytes (128 hex characters)
    assert len(wallet.public_key) == 128

    # Verify keys are hexadecimal strings
    int(wallet.private_key, 16)
    int(wallet.public_key, 16)


def test_wallet_uniqueness() -> None:
    wallet1 = Wallet()
    wallet2 = Wallet()

    assert wallet1.private_key != wallet2.private_key
    assert wallet1.public_key != wallet2.public_key
