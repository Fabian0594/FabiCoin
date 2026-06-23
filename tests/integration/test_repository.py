import os

from infrastructure.file_repository import FileBlockchainRepository


def test_file_blockchain_repository_save_and_load(tmp_path) -> None:
    """Verifies that FileBlockchainRepository correctly saves and loads
    the blockchain state.
    """

    test_file = tmp_path / "test_node_state.json"
    repo = FileBlockchainRepository(file_path=str(test_file))

    # Initially, the file doesn't exist, so load_state should return None
    assert repo.load_state() is None

    # Save a mock state
    mock_chain = [{"index": 0, "hash": "genesis"}]
    mock_mempool = [{"sender": "NETWORK", "recipient": "miner", "amount": 10.0}]
    repo.save_state(mock_chain, mock_mempool)

    # File should exist now
    assert os.path.exists(test_file)

    # Load the state and verify it matches the saved data
    loaded_state = repo.load_state()
    assert loaded_state is not None
    loaded_chain, loaded_mempool = loaded_state
    assert loaded_chain == mock_chain
    assert loaded_mempool == mock_mempool
