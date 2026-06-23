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
