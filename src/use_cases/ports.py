from abc import ABC, abstractmethod


class BlockchainRepository(ABC):
    """Abstract port representing the persistence repository for the blockchain state.

    Decouples the application layer from the database technology details.
    """

    @abstractmethod
    def save_state(self, chain_data: list, unconfirmed_txs: list) -> None:
        """Saves the current blockchain state (chain and mempool)."""
        pass

    @abstractmethod
    def load_state(self) -> tuple[list, list] | None:
        """Loads and returns the saved state if it exists, otherwise returns None."""
        pass
