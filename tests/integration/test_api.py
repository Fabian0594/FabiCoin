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
