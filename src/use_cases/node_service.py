from typing import Any, Dict, List, Optional

import httpx

from domain.block import Block
from domain.blockchain import Blockchain
from domain.transaction import Transaction
from domain.wallet import Wallet
from use_cases.ports import BlockchainRepository


class NodeService:
    """Application service that orchestrates the state of a blockchain node.

    It holds the blockchain instance and the resident miner's wallet.
    """

    def __init__(self, repository: Optional[BlockchainRepository] = None) -> None:
        self.blockchain = Blockchain()
        self.wallet = Wallet()
        self.repository = repository

        if self.repository is not None:
            state = self.repository.load_state()
            if state is not None:
                chain_data, mempool_data = state
                self.blockchain._chain = [Block.from_dict(b) for b in chain_data]
                self.blockchain._unconfirmed_transactions = [
                    Transaction.from_dict(tx) for tx in mempool_data
                ]

    def get_chain(self) -> List[Dict[str, Any]]:
        """Returns the complete blockchain representation as a list of dictionaries."""
        chain_data = []
        for block in self.blockchain.chain:
            block_dict = {
                "index": block.index,
                "timestamp": block.timestamp,
                "transactions": [
                    {
                        "sender": tx.sender,
                        "recipient": tx.recipient,
                        "amount": tx.amount,
                        "timestamp": tx.timestamp,
                        "id": tx.id,
                        "signature": tx.signature,
                    }
                    for tx in block.transactions
                ],
                "previous_hash": block.previous_hash,
                "nonce": block.nonce,
                "hash": block.hash,
            }
            chain_data.append(block_dict)
        return chain_data

    def register_nodes(self, nodes: List[str]) -> None:
        """Registers a list of peer nodes in the blockchain."""
        for node in nodes:
            self.blockchain.register_node(node)

    def resolve_conflicts(self) -> bool:
        """Resolves conflicts by replacing our chain with the longest valid chain."""
        new_chain = None
        max_length = len(self.blockchain.chain)

        for node in self.blockchain.nodes:
            try:
                response = httpx.get(f"{node}/chain", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    length = data.get("length", 0)
                    chain = data.get("chain", [])

                    if length > max_length:
                        reconstructed = [
                            Block.from_dict(block_dict) for block_dict in chain
                        ]

                        # Validate reconstructed chain
                        temp_chain = Blockchain()
                        temp_chain._chain = reconstructed
                        if temp_chain.is_chain_valid():
                            max_length = length
                            new_chain = reconstructed
            except Exception:
                continue

        if new_chain is not None:
            self.blockchain._chain = new_chain
            self.save_to_repository()
            return True

        return False

    def submit_transaction(self, tx_data: dict) -> None:
        """Instantiates a Transaction from a dictionary and adds it to the mempool.

        Raises:
            ValueError: If the transaction is invalid, unsigned, or has
                insufficient funds.
        """
        try:
            tx = Transaction.from_dict(tx_data)
            self.blockchain.add_new_transaction(tx)
            self.save_to_repository()
        except ValueError as e:
            raise ValueError(str(e)) from e

    def save_to_repository(self) -> None:
        """Saves the current state of the blockchain to the repository, if available."""
        if self.repository is not None:
            chain_data = self.get_chain()
            mempool_data = [
                {
                    "sender": tx.sender,
                    "recipient": tx.recipient,
                    "amount": tx.amount,
                    "timestamp": tx.timestamp,
                    "id": tx.id,
                    "signature": tx.signature,
                }
                for tx in self.blockchain.unconfirmed_transactions
            ]
            self.repository.save_state(chain_data, mempool_data)

    def mine(self) -> bool:
        """Mines unconfirmed transactions using the resident wallet's public key.

        If mining is successful, persists the new state.
        """
        miner_address = self.wallet.public_key
        success = self.blockchain.mine_unconfirmed_transactions(miner_address)
        if success:
            self.save_to_repository()
        return success
