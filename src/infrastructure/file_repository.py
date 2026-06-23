import json
import os

from use_cases.ports import BlockchainRepository


class FileBlockchainRepository(BlockchainRepository):
    """Concrete implementation of BlockchainRepository that persists state
    to a JSON file on disk.
    """

    def __init__(self, file_path: str = "data/node_state.json") -> None:
        self.file_path = file_path
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def save_state(self, chain_data: list, unconfirmed_txs: list) -> None:
        """Saves the current blockchain state (chain and mempool) to a JSON file."""
        state = {
            "chain": chain_data,
            "mempool": unconfirmed_txs,
        }
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)

    def load_state(self) -> tuple[list, list] | None:
        """Loads and returns the saved state if it exists, otherwise returns None."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                state = json.load(f)
                chain = state.get("chain", [])
                mempool = state.get("mempool", [])
                return chain, mempool
        except FileNotFoundError:
            return None
