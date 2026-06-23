import time

import pytest

from domain.block import Block
from domain.blockchain import Blockchain
from domain.transaction import Transaction
from domain.wallet import Wallet


def create_valid_transaction(
    sender: Wallet, recipient: Wallet, amount: float
) -> Transaction:
    now = time.time()
    tx_id = Transaction.calculate_hash(
        sender.public_key, recipient.public_key, amount, now
    )
    tx = Transaction(
        sender=sender.public_key,
        recipient=recipient.public_key,
        amount=amount,
        timestamp=now,
        id=tx_id,
    )
    tx.sign_transaction(sender.private_key)
    return tx


def bootstrap_wallet_balance(
    blockchain: Blockchain, wallet: Wallet, amount: float
) -> None:
    latest = blockchain.get_latest_block()
    now = time.time()
    coinbase_tx = Transaction(
        sender="NETWORK",
        recipient=wallet.public_key,
        amount=amount,
        timestamp=now,
        id=Transaction.calculate_hash("NETWORK", wallet.public_key, amount, now),
    )
    new_index = len(blockchain.chain)
    new_hash = Block.calculate_hash(new_index, now, [coinbase_tx], latest.hash, 0)
    block = Block(
        index=new_index,
        timestamp=now,
        transactions=[coinbase_tx],
        previous_hash=latest.hash,
        nonce=0,
        hash=new_hash,
    )
    block.mine(blockchain.difficulty)
    blockchain.add_block(block)


def test_blockchain_initialization_creates_genesis_block() -> None:
    blockchain = Blockchain()

    assert len(blockchain.chain) == 1
    genesis = blockchain.chain[0]
    assert genesis.index == 0
    assert genesis.transactions == []
    assert genesis.previous_hash == "0"
    assert genesis.nonce == 0
    # The hash should be valid and recalculatable
    expected_hash = Block.calculate_hash(
        genesis.index,
        genesis.timestamp,
        genesis.transactions,
        genesis.previous_hash,
        genesis.nonce,
    )
    assert genesis.hash == expected_hash


def test_get_latest_block() -> None:
    blockchain = Blockchain()
    latest = blockchain.get_latest_block()

    assert latest == blockchain.chain[0]  # Initially it's the genesis block


def test_add_block() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()

    w1 = Wallet()
    w2 = Wallet()
    tx = create_valid_transaction(w1, w2, 5.0)

    new_timestamp = time.time()
    transactions = [tx]
    new_index = 1
    new_nonce = 42

    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )

    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=new_hash,
    )

    blockchain.add_block(new_block)

    assert len(blockchain.chain) == 2
    assert blockchain.get_latest_block() == new_block
    assert blockchain.chain[1] == new_block


def test_add_block_invalid_previous_hash() -> None:
    blockchain = Blockchain()
    new_timestamp = time.time()
    w1 = Wallet()
    w2 = Wallet()
    tx = create_valid_transaction(w1, w2, 5.0)
    transactions = [tx]
    new_index = 1
    new_nonce = 42

    # Wrong previous hash
    wrong_previous_hash = "wrong_hash"
    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=wrong_previous_hash,
        nonce=new_nonce,
    )

    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=wrong_previous_hash,
        nonce=new_nonce,
        hash=new_hash,
    )

    with pytest.raises(ValueError, match="Bloque inválido: previous_hash incorrecto"):
        blockchain.add_block(new_block)


def test_add_block_invalid_hash() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()
    new_timestamp = time.time()
    w1 = Wallet()
    w2 = Wallet()
    tx = create_valid_transaction(w1, w2, 5.0)
    transactions = [tx]
    new_index = 1
    new_nonce = 42

    # Wrong block hash
    wrong_hash = "wrong_hash"
    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=wrong_hash,
    )

    with pytest.raises(ValueError, match="Bloque inválido: hash incorrecto"):
        blockchain.add_block(new_block)


def test_blockchain_newly_created_is_valid() -> None:
    blockchain = Blockchain()
    assert blockchain.is_chain_valid() is True


def test_blockchain_immutability_tampered_data() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()

    new_timestamp = time.time()
    w1 = Wallet()
    w2 = Wallet()
    tx = create_valid_transaction(w1, w2, 10.0)
    transactions = [tx]
    new_index = 1
    new_nonce = 100
    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )
    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=new_hash,
    )
    blockchain.add_block(new_block)

    assert blockchain.is_chain_valid() is True

    # Tamper with the block transactions (changing the list)
    tampered_tx = create_valid_transaction(w1, w2, 999.0)
    new_block.transactions = [tampered_tx]

    assert blockchain.is_chain_valid() is False


def test_blockchain_immutability_tampered_previous_hash() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()

    new_timestamp = time.time()
    w1 = Wallet()
    w2 = Wallet()
    tx = create_valid_transaction(w1, w2, 10.0)
    transactions = [tx]
    new_index = 1
    new_nonce = 100
    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )
    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=new_hash,
    )
    blockchain.add_block(new_block)

    assert blockchain.is_chain_valid() is True

    # Tamper with previous_hash and update current hash to satisfy Invariant 1
    new_block.previous_hash = "wrong_previous_hash"
    new_block.hash = Block.calculate_hash(
        new_block.index,
        new_block.timestamp,
        new_block.transactions,
        new_block.previous_hash,
        new_block.nonce,
    )

    assert blockchain.is_chain_valid() is False


def test_add_new_transaction_to_mempool() -> None:
    blockchain = Blockchain()
    assert blockchain.unconfirmed_transactions == []

    w1 = Wallet()
    w2 = Wallet()
    # Bootstrap sender balance to avoid overdraft rejection
    bootstrap_wallet_balance(blockchain, w1, 20.0)

    tx = create_valid_transaction(w1, w2, 15.0)
    blockchain.add_new_transaction(tx)

    assert len(blockchain.unconfirmed_transactions) == 1
    assert blockchain.unconfirmed_transactions[0] == tx


def test_add_new_transaction_unsigned_raises_error() -> None:
    blockchain = Blockchain()
    w1 = Wallet()
    w2 = Wallet()
    bootstrap_wallet_balance(blockchain, w1, 20.0)

    now = time.time()
    tx_id = Transaction.calculate_hash(w1.public_key, w2.public_key, 10.0, now)
    unsigned_tx = Transaction(
        sender=w1.public_key,
        recipient=w2.public_key,
        amount=10.0,
        timestamp=now,
        id=tx_id,
    )

    with pytest.raises(ValueError, match="Transacción inválida o firma incorrecta"):
        blockchain.add_new_transaction(unsigned_tx)


def test_add_new_transaction_tampered_signature_raises_error() -> None:
    blockchain = Blockchain()
    w1 = Wallet()
    w2 = Wallet()
    bootstrap_wallet_balance(blockchain, w1, 20.0)

    tx = create_valid_transaction(w1, w2, 10.0)
    tx.signature = "f" * len(tx.signature)

    with pytest.raises(ValueError, match="Transacción inválida o firma incorrecta"):
        blockchain.add_new_transaction(tx)


def test_blockchain_default_configurations() -> None:
    blockchain = Blockchain()
    assert blockchain.mining_reward == 10.0
    assert blockchain.difficulty == 2


def test_mine_unconfirmed_transactions() -> None:
    blockchain = Blockchain()

    # Mining empty mempool should return False
    assert blockchain.mine_unconfirmed_transactions("miner_bob") is False
    assert len(blockchain.chain) == 1

    # Bootstrap senders
    w1 = Wallet()
    w2 = Wallet()
    bootstrap_wallet_balance(blockchain, w1, 10.0)
    bootstrap_wallet_balance(blockchain, w2, 10.0)

    # Add 2 valid transactions
    tx1 = create_valid_transaction(w1, w2, 5.0)
    tx2 = create_valid_transaction(w2, w1, 3.0)

    blockchain.add_new_transaction(tx1)
    blockchain.add_new_transaction(tx2)

    assert len(blockchain.unconfirmed_transactions) == 2

    # Mine the transactions
    success = blockchain.mine_unconfirmed_transactions("miner_bob")
    assert success is True

    # Check chain growth
    # Chain: genesis (1), bootstrap w1 (2), bootstrap w2 (3), mine (4)
    assert len(blockchain.chain) == 4
    new_block = blockchain.get_latest_block()
    assert new_block.index == 3

    # Check block transactions (should have 3: tx1, tx2, and coinbase)
    assert len(new_block.transactions) == 3
    assert new_block.transactions[0] == tx1
    assert new_block.transactions[1] == tx2

    coinbase = new_block.transactions[2]
    assert coinbase.sender == "NETWORK"
    assert coinbase.recipient == "miner_bob"
    assert coinbase.amount == blockchain.mining_reward

    # Check mempool is cleared
    assert len(blockchain.unconfirmed_transactions) == 0

    # Check blockchain validity
    assert blockchain.is_chain_valid() is True


def test_add_block_rejects_block_with_unsigned_transaction() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()

    w1 = Wallet()
    w2 = Wallet()
    now = time.time()
    tx_id = Transaction.calculate_hash(w1.public_key, w2.public_key, 10.0, now)
    unsigned_tx = Transaction(
        sender=w1.public_key,
        recipient=w2.public_key,
        amount=10.0,
        timestamp=now,
        id=tx_id,
    )

    new_timestamp = time.time()
    transactions = [unsigned_tx]
    new_index = 1
    new_nonce = 42

    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )

    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=new_hash,
    )

    with pytest.raises(ValueError, match="Bloque con firmas inválidas o sin firmar"):
        blockchain.add_block(new_block)


def test_add_block_rejects_block_with_tampered_signature() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()

    w1 = Wallet()
    w2 = Wallet()
    tx = create_valid_transaction(w1, w2, 10.0)
    tx.signature = "f" * len(tx.signature)

    new_timestamp = time.time()
    transactions = [tx]
    new_index = 1
    new_nonce = 42

    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )

    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=new_hash,
    )

    with pytest.raises(ValueError, match="Bloque con firmas inválidas o sin firmar"):
        blockchain.add_block(new_block)


def test_blockchain_get_balance() -> None:
    blockchain = Blockchain()

    w1 = Wallet()
    w2 = Wallet()
    w3 = Wallet()

    # Initial balances are 0.0
    assert blockchain.get_balance(w1.public_key) == 0.0
    assert blockchain.get_balance(w2.public_key) == 0.0
    assert blockchain.get_balance(w3.public_key) == 0.0

    # Bootstrap w1 with 20.0 coins
    bootstrap_wallet_balance(blockchain, w1, 20.0)
    assert blockchain.get_balance(w1.public_key) == 20.0

    # w1 sends 15.0 coins to w2
    tx1 = create_valid_transaction(w1, w2, 15.0)
    blockchain.add_new_transaction(tx1)

    # Balance shouldn't change yet as the transaction is unconfirmed
    assert blockchain.get_balance(w1.public_key) == 20.0
    assert blockchain.get_balance(w2.public_key) == 0.0

    # Mine block 1 (w3 is the miner)
    blockchain.mine_unconfirmed_transactions(w3.public_key)

    # Check balances after block 1
    assert blockchain.get_balance(w1.public_key) == 5.0  # 20.0 - 15.0
    assert blockchain.get_balance(w2.public_key) == 15.0
    assert blockchain.get_balance(w3.public_key) == 10.0  # Coinbase reward

    # w2 sends 5.0 coins to w1
    tx2 = create_valid_transaction(w2, w1, 5.0)
    blockchain.add_new_transaction(tx2)

    # Mine block 2 (w3 is the miner again)
    blockchain.mine_unconfirmed_transactions(w3.public_key)

    # Check balances after block 2
    assert blockchain.get_balance(w1.public_key) == 10.0  # 5.0 + 5.0
    assert blockchain.get_balance(w2.public_key) == 10.0  # 15.0 - 5.0
    assert blockchain.get_balance(w3.public_key) == 20.0  # Two rewards


def test_add_new_transaction_insufficient_funds() -> None:
    blockchain = Blockchain()
    w1 = Wallet()
    w2 = Wallet()

    # w1 has 0 balance, tries to send 5.0
    tx = create_valid_transaction(w1, w2, 5.0)
    with pytest.raises(ValueError, match="Fondos insuficientes"):
        blockchain.add_new_transaction(tx)


def test_add_new_transaction_double_spending_mempool() -> None:
    blockchain = Blockchain()
    w1 = Wallet()
    w2 = Wallet()
    w3 = Wallet()

    # Bootstrap w1 with 10.0 coins
    bootstrap_wallet_balance(blockchain, w1, 10.0)

    # w1 sends 6.0 to w2 (allowed, remaining available: 4.0)
    tx1 = create_valid_transaction(w1, w2, 6.0)
    blockchain.add_new_transaction(tx1)

    # w1 tries to send 5.0 to w3 (should fail due to pending 6.0 tx)
    tx2 = create_valid_transaction(w1, w3, 5.0)
    with pytest.raises(ValueError, match="Fondos insuficientes"):
        blockchain.add_new_transaction(tx2)
