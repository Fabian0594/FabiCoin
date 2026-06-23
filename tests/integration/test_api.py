from unittest.mock import patch

from fastapi.testclient import TestClient

from presentation.api import app

client = TestClient(app)


def test_get_chain() -> None:
    response = client.get("/chain")
    assert response.status_code == 200
    data = response.json()

    assert "length" in data
    assert "chain" in data
    assert data["length"] == 1
    assert data["chain"][0]["index"] == 0
    assert data["chain"][0]["previous_hash"] == "0"


def test_register_nodes() -> None:
    payload = {"nodes": ["http://127.0.0.1:8001", "http://127.0.0.1:8002"]}
    response = client.post("/nodes/register", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "total_nodes" in data
    assert "http://127.0.0.1:8001" in data["total_nodes"]
    assert "http://127.0.0.1:8002" in data["total_nodes"]
    assert len(data["total_nodes"]) == 2


@patch("presentation.api.node_service.resolve_conflicts")
@patch("presentation.api.node_service.get_chain")
def test_resolve_conflicts_replaced(mock_get_chain, mock_resolve_conflicts) -> None:
    mock_resolve_conflicts.return_value = True
    mock_get_chain.return_value = [
        {"index": 0, "hash": "genesis"},
        {"index": 1, "hash": "new_block"},
    ]

    response = client.get("/nodes/resolve")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Nuestra cadena fue reemplazada"
    assert len(data["chain"]) == 2
    assert data["chain"][1]["index"] == 1


@patch("presentation.api.node_service.resolve_conflicts")
@patch("presentation.api.node_service.get_chain")
def test_resolve_conflicts_not_replaced(mock_get_chain, mock_resolve_conflicts) -> None:
    mock_resolve_conflicts.return_value = False
    mock_get_chain.return_value = [{"index": 0, "hash": "genesis"}]

    response = client.get("/nodes/resolve")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Nuestra cadena es la autoridad (la más larga)"
    assert len(data["chain"]) == 1


@patch("presentation.api.node_service.submit_transaction")
def test_new_transaction_success(mock_submit) -> None:
    payload = {
        "sender": "sender_address",
        "recipient": "recipient_address",
        "amount": 10.0,
        "timestamp": 1600000000.0,
        "id": "tx_id",
        "signature": "signature_hex",
    }
    response = client.post("/transactions/new", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Transacción añadida a la mempool"}
    mock_submit.assert_called_once_with(payload)


@patch("presentation.api.node_service.submit_transaction")
def test_new_transaction_invalid(mock_submit) -> None:
    mock_submit.side_effect = ValueError("Fondos insuficientes")
    payload = {
        "sender": "sender_address",
        "recipient": "recipient_address",
        "amount": 10.0,
        "timestamp": 1600000000.0,
        "id": "tx_id",
        "signature": "signature_hex",
    }
    response = client.post("/transactions/new", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Fondos insuficientes"


@patch("presentation.api.node_service.blockchain.mine_unconfirmed_transactions")
def test_mine_no_transactions(mock_mine) -> None:
    mock_mine.return_value = False
    response = client.get("/mine")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No hay transacciones para minar"


@patch("presentation.api.node_service.blockchain.get_latest_block")
@patch("presentation.api.node_service.blockchain.mine_unconfirmed_transactions")
def test_mine_success(mock_mine, mock_get_latest_block) -> None:
    mock_mine.return_value = True

    # Mock block with transactions
    from domain.block import Block
    from domain.transaction import Transaction

    tx = Transaction(
        sender="NETWORK",
        recipient="miner_address",
        amount=10.0,
        timestamp=1600000000.0,
        id="tx_id",
        signature="",
    )
    mock_block = Block(
        index=1,
        timestamp=1600000000.0,
        transactions=[tx],
        previous_hash="genesis_hash",
        nonce=42,
        hash="block_hash",
    )
    mock_get_latest_block.return_value = mock_block

    response = client.get("/mine")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Nuevo bloque minado con éxito"
    assert data["block"]["index"] == 1
    assert data["block"]["hash"] == "block_hash"
    assert len(data["block"]["transactions"]) == 1


def test_e2e_transaction_and_mine() -> None:
    """E2E test verifying transaction submission, mining, and state changes."""
    import time

    import presentation.api
    from domain.transaction import Transaction
    from domain.wallet import Wallet
    from use_cases.node_service import NodeService

    # Re-initialize node_service to ensure a clean state
    presentation.api.node_service = NodeService()

    # 1. Create local test wallets
    sender_wallet = Wallet()
    recipient_wallet = Wallet()

    # 2. Mine a block with a coinbase tx to fund the sender_wallet
    timestamp1 = time.time()
    coinbase_tx_id = Transaction.calculate_hash(
        sender="NETWORK",
        recipient=sender_wallet.public_key,
        amount=50.0,
        timestamp=timestamp1,
    )
    payload1 = {
        "sender": "NETWORK",
        "recipient": sender_wallet.public_key,
        "amount": 50.0,
        "timestamp": timestamp1,
        "id": coinbase_tx_id,
        "signature": "",
    }
    response = client.post("/transactions/new", json=payload1)
    assert response.status_code == 200

    response = client.get("/mine")
    assert response.status_code == 200

    # 3. Create a valid signed transaction from sender_wallet to recipient_wallet
    timestamp2 = time.time()
    tx = Transaction(
        sender=sender_wallet.public_key,
        recipient=recipient_wallet.public_key,
        amount=20.0,
        timestamp=timestamp2,
        id="",
    )
    tx.id = Transaction.calculate_hash(tx.sender, tx.recipient, tx.amount, tx.timestamp)
    tx.sign_transaction(sender_wallet.private_key)

    payload2 = {
        "sender": tx.sender,
        "recipient": tx.recipient,
        "amount": tx.amount,
        "timestamp": tx.timestamp,
        "id": tx.id,
        "signature": tx.signature,
    }
    response = client.post("/transactions/new", json=payload2)
    assert response.status_code == 200

    # 4. Mine the transaction and verify chain length
    response = client.get("/mine")
    assert response.status_code == 200

    response = client.get("/chain")
    assert response.status_code == 200
    data = response.json()
    assert data["length"] == 3

    # 5. Verify balances
    assert (
        presentation.api.node_service.blockchain.get_balance(sender_wallet.public_key)
        == 30.0
    )
    assert (
        presentation.api.node_service.blockchain.get_balance(
            recipient_wallet.public_key
        )
        == 20.0
    )

    # Re-initialize again to leave a clean state for subsequent tests
    presentation.api.node_service = NodeService()
