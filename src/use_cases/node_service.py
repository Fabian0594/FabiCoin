from typing import Any, Dict, List

from domain.blockchain import Blockchain
from domain.wallet import Wallet


class NodeService:
    """Application service that orchestrates the state of a blockchain node.

    It holds the blockchain instance and the resident miner's wallet.
    """

    def __init__(self) -> None:
        self.blockchain = Blockchain()
        self.wallet = Wallet()

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
