import hashlib
from typing import List

from domain.transaction import Transaction


def build_merkle_root(transactions: List[Transaction]) -> str:
    """Calculates the Merkle Root hash from a list of transactions.

    If the list is empty, returns the SHA-256 hash of an empty byte string.
    If a level has an odd number of nodes, the last node is duplicated.
    """
    if not transactions:
        return hashlib.sha256(b"").hexdigest()

    # Leaf nodes are the transaction IDs
    nodes = [tx.id for tx in transactions]

    while len(nodes) > 1:
        next_level = []
        for i in range(0, len(nodes), 2):
            node_a = nodes[i]
            # If there is no right child, duplicate the left child (node_a)
            node_b = nodes[i + 1] if (i + 1) < len(nodes) else node_a

            combined = node_a + node_b
            parent_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
            next_level.append(parent_hash)
        nodes = next_level

    return nodes[0]
