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
