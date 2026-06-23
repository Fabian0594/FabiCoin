from unittest.mock import MagicMock, patch

from domain.block import Block
from domain.blockchain import Blockchain
from domain.transaction import Transaction
from domain.wallet import Wallet
from use_cases.node_service import NodeService


def test_node_service_initialization() -> None:
    service = NodeService()

    assert service.blockchain is not None
    assert service.wallet is not None
    assert len(service.blockchain.chain) == 1
    assert len(service.wallet.private_key) == 64
    assert len(service.wallet.public_key) == 128


def test_node_service_get_chain() -> None:
    service = NodeService()
    chain_data = service.get_chain()

    assert isinstance(chain_data, list)
    assert len(chain_data) == 1

    genesis_block = chain_data[0]
    assert isinstance(genesis_block, dict)
    assert genesis_block["index"] == 0
    assert genesis_block["previous_hash"] == "0"
    assert genesis_block["nonce"] == 0
    assert isinstance(genesis_block["hash"], str)
    assert genesis_block["transactions"] == []
    assert "timestamp" in genesis_block


def test_resolve_conflicts_no_nodes() -> None:
    service = NodeService()
    assert service.resolve_conflicts() is False


@patch("httpx.get")
def test_resolve_conflicts_shorter_or_equal_chain(mock_get: MagicMock) -> None:
    service = NodeService()
    service.register_nodes(["http://127.0.0.1:8001"])

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "length": 1,
        "chain": service.get_chain(),
    }
    mock_get.return_value = mock_response

    assert service.resolve_conflicts() is False
    assert len(service.blockchain.chain) == 1


@patch("httpx.get")
def test_resolve_conflicts_longer_valid_chain(mock_get: MagicMock) -> None:
    service = NodeService()
    service.register_nodes(["http://127.0.0.1:8001"])

    # Create a valid longer chain
    neighbor_blockchain = Blockchain()
    w1 = Wallet()
    w2 = Wallet()
    tx = Transaction(
        sender=w1.public_key,
        recipient=w2.public_key,
        amount=5.0,
        timestamp=1600000000.0,
        id="tx_id",
        signature="",
    )
    tx.sign_transaction(w1.private_key)

    import time

    new_timestamp = time.time()
    new_index = 1
    new_nonce = 42
    new_hash = Block.calculate_hash(
        new_index,
        new_timestamp,
        [tx],
        neighbor_blockchain.get_latest_block().hash,
        new_nonce,
    )
    new_block = Block(
        new_index,
        new_timestamp,
        [tx],
        neighbor_blockchain.get_latest_block().hash,
        new_nonce,
        new_hash,
    )
    new_block.mine(neighbor_blockchain.difficulty)
    neighbor_blockchain.add_block(new_block)

    # Get neighbor chain representation
    neighbor_service = NodeService()
    neighbor_service.blockchain = neighbor_blockchain
    neighbor_chain_data = neighbor_service.get_chain()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "length": 2,
        "chain": neighbor_chain_data,
    }
    mock_get.return_value = mock_response

    # Resolve conflicts should return True (replaced)
    assert service.resolve_conflicts() is True
    assert len(service.blockchain.chain) == 2
    assert service.blockchain.get_latest_block().hash == new_block.hash


@patch("httpx.get")
def test_resolve_conflicts_longer_invalid_chain(mock_get: MagicMock) -> None:
    service = NodeService()
    service.register_nodes(["http://127.0.0.1:8001"])

    # Create an invalid longer chain (wrong previous_hash)
    neighbor_service = NodeService()
    w1 = Wallet()
    w2 = Wallet()
    tx = Transaction(
        sender=w1.public_key,
        recipient=w2.public_key,
        amount=5.0,
        timestamp=1600000000.0,
        id="tx_id",
        signature="",
    )
    tx.sign_transaction(w1.private_key)

    import time

    new_timestamp = time.time()
    new_index = 1
    new_nonce = 42
    new_hash = Block.calculate_hash(
        new_index, new_timestamp, [tx], "wrong_prev_hash", new_nonce
    )
    new_block = Block(
        new_index,
        new_timestamp,
        [tx],
        "wrong_prev_hash",
        new_nonce,
        new_hash,
    )
    new_block.mine(service.blockchain.difficulty)

    # Bypass add_block verification by appending directly to mock list
    neighbor_service.blockchain._chain.append(new_block)
    neighbor_chain_data = neighbor_service.get_chain()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "length": 2,
        "chain": neighbor_chain_data,
    }
    mock_get.return_value = mock_response

    # Resolve conflicts should return False (invalid chain)
    assert service.resolve_conflicts() is False
    assert len(service.blockchain.chain) == 1


def test_submit_transaction_success() -> None:
    service = NodeService()
    # Coinbase transaction (sender="NETWORK") is valid without a signature
    tx_data = {
        "sender": "NETWORK",
        "recipient": "recipient_address",
        "amount": 10.0,
        "timestamp": 1600000000.0,
        "id": "tx_id",
        "signature": "",
    }
    service.submit_transaction(tx_data)
    assert len(service.blockchain.unconfirmed_transactions) == 1
    assert (
        service.blockchain.unconfirmed_transactions[0].recipient == "recipient_address"
    )


def test_submit_transaction_invalid() -> None:
    service = NodeService()
    # Non-coinbase transaction without signature raises ValueError
    tx_data = {
        "sender": "some_sender",
        "recipient": "recipient_address",
        "amount": 10.0,
        "timestamp": 1600000000.0,
        "id": "tx_id",
        "signature": "",
    }
    import pytest

    with pytest.raises(ValueError):
        service.submit_transaction(tx_data)
    assert len(service.blockchain.unconfirmed_transactions) == 0
