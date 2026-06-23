import time
from typing import List

from domain.block import Block
from domain.transaction import Transaction


class Blockchain:
    """Represents a blockchain that manages a chain of blocks.

    It automatically initializes with a Genesis block.
    """

    def __init__(self) -> None:
        self._chain: List[Block] = []
        self._unconfirmed_transactions: List[Transaction] = []
        self.mining_reward = 10.0
        self.difficulty = 2
        self.nodes = set()
        self._create_genesis_block()

    @property
    def chain(self) -> List[Block]:
        """Returns the list of blocks in the chain."""
        return self._chain

    @property
    def unconfirmed_transactions(self) -> List[Transaction]:
        """Returns the list of unconfirmed transactions (mempool)."""
        return self._unconfirmed_transactions

    def _create_genesis_block(self) -> None:
        # Create genesis block with index 0 and previous_hash "0"
        timestamp = time.time()
        transactions: List[Transaction] = []
        previous_hash = "0"
        nonce = 0
        genesis_hash = Block.calculate_hash(
            index=0,
            timestamp=timestamp,
            transactions=transactions,
            previous_hash=previous_hash,
            nonce=nonce,
        )
        genesis_block = Block(
            index=0,
            timestamp=timestamp,
            transactions=transactions,
            previous_hash=previous_hash,
            nonce=nonce,
            hash=genesis_hash,
        )
        self._chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        """Returns the last block added to the chain."""
        return self._chain[-1]

    def add_block(self, new_block: Block) -> None:
        """Appends a new, pre-mined block to the chain.

        Raises:
            ValueError: If the block is invalid (hash or previous_hash is incorrect).
        """
        latest_block = self.get_latest_block()

        # Invariant 1: previous_hash must match the latest block's hash
        if new_block.previous_hash != latest_block.hash:
            raise ValueError("Bloque inválido: previous_hash incorrecto.")

        # Invariant 2: hash must match the recalculated hash of block state
        recalculated_hash = Block.calculate_hash(
            new_block.index,
            new_block.timestamp,
            new_block.transactions,
            new_block.previous_hash,
            new_block.nonce,
        )
        if new_block.hash != recalculated_hash:
            raise ValueError("Bloque inválido: hash incorrecto.")

        # Invariant 3: all transactions in the block must be valid
        for tx in new_block.transactions:
            try:
                if not tx.is_valid():
                    raise ValueError("Bloque inválido: firma incorrecta.")
            except ValueError as e:
                raise ValueError("Bloque con firmas inválidas o sin firmar.") from e

        self._chain.append(new_block)

    def add_new_transaction(self, transaction: Transaction) -> None:
        """Adds a new transaction to the mempool (unconfirmed transactions list).

        Raises:
            ValueError: If the transaction is invalid, unsigned, or if there are
                insufficient funds.
        """
        try:
            if not transaction.is_valid():
                raise ValueError("Transacción inválida o firma incorrecta")
        except ValueError as e:
            raise ValueError("Transacción inválida o firma incorrecta") from e

        # Double spending and overdraft protection
        if transaction.sender != "NETWORK":
            current_balance = self.get_balance(transaction.sender)
            committed_in_mempool = sum(
                tx.amount
                for tx in self._unconfirmed_transactions
                if tx.sender == transaction.sender
            )
            available_balance = current_balance - committed_in_mempool
            if available_balance < transaction.amount:
                raise ValueError("Fondos insuficientes")

        self._unconfirmed_transactions.append(transaction)

    def mine_unconfirmed_transactions(self, miner_address: str) -> bool:
        """Mines mempool transactions, rewards miner, and clears mempool."""
        if not self._unconfirmed_transactions:
            return False

        # Create coinbase transaction
        coinbase_timestamp = time.time()
        coinbase_hash = Transaction.calculate_hash(
            sender="NETWORK",
            recipient=miner_address,
            amount=self.mining_reward,
            timestamp=coinbase_timestamp,
        )
        coinbase_tx = Transaction(
            sender="NETWORK",
            recipient=miner_address,
            amount=self.mining_reward,
            timestamp=coinbase_timestamp,
            id=coinbase_hash,
        )

        # Combine with unconfirmed transactions
        transactions_to_mine = self._unconfirmed_transactions + [coinbase_tx]

        # Create new block
        new_block = Block(
            index=len(self._chain),
            timestamp=time.time(),
            transactions=transactions_to_mine,
            previous_hash=self.get_latest_block().hash,
            nonce=0,
            hash="",
        )

        # Mine the block (Proof of Work)
        new_block.mine(self.difficulty)

        # Add the block to the chain (which validates it)
        self.add_block(new_block)

        # Clear the mempool
        self._unconfirmed_transactions = []
        return True

    def get_balance(self, address: str) -> float:
        """Calculates the balance of a given address by scanning all transactions."""
        balance = 0.0
        for block in self._chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        return balance

    def register_node(self, address: str) -> None:
        """Registers a new peer node by adding its address to the set."""
        self.nodes.add(address)

    def is_chain_valid(self) -> bool:
        """Validates the immutability and integrity of the blockchain."""
        if not self._chain:
            return False

        # Validate genesis block hash
        genesis = self._chain[0]
        recalculated_genesis_hash = Block.calculate_hash(
            genesis.index,
            genesis.timestamp,
            genesis.transactions,
            genesis.previous_hash,
            genesis.nonce,
        )
        if genesis.hash != recalculated_genesis_hash:
            return False

        # Validate subsequent blocks
        for i in range(1, len(self._chain)):
            current = self._chain[i]
            previous = self._chain[i - 1]

            # Invariant 1: Hash must match recalculated hash of attributes
            recalculated_hash = Block.calculate_hash(
                current.index,
                current.timestamp,
                current.transactions,
                current.previous_hash,
                current.nonce,
            )
            if current.hash != recalculated_hash:
                return False

            # Invariant 2: Current previous_hash must match previous block's hash
            if current.previous_hash != previous.hash:
                return False

        return True
