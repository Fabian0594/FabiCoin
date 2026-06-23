from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from infrastructure.file_repository import FileBlockchainRepository
from use_cases.node_service import NodeService

app = FastAPI(title="FabiCoin Node API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción limitaremos esto a la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
repo = FileBlockchainRepository()
node_service = NodeService(repository=repo)


class RegisterNodesRequest(BaseModel):
    nodes: List[str]


class TransactionRequest(BaseModel):
    sender: str
    recipient: str
    amount: float
    timestamp: float
    id: str
    signature: str


class LocalTransferRequest(BaseModel):
    recipient: str
    amount: float


@app.get("/chain")
def get_chain() -> dict:
    """GET endpoint to retrieve the complete blockchain."""
    chain_data = node_service.get_chain()
    return {"length": len(chain_data), "chain": chain_data}


@app.post("/nodes/register")
def register_nodes(request: RegisterNodesRequest) -> dict:
    """POST endpoint to register new peer nodes in the network."""
    node_service.register_nodes(request.nodes)
    return {
        "message": "Nodos registrados con éxito",
        "total_nodes": list(node_service.blockchain.nodes),
    }


@app.get("/nodes/resolve")
def resolve_conflicts() -> dict:
    """GET endpoint to trigger consensus conflict resolution."""
    replaced = node_service.resolve_conflicts()
    chain_data = node_service.get_chain()
    if replaced:
        return {
            "message": "Nuestra cadena fue reemplazada",
            "chain": chain_data,
        }
    return {
        "message": "Nuestra cadena es la autoridad (la más larga)",
        "chain": chain_data,
    }


@app.post("/transactions/new")
def new_transaction(request: TransactionRequest) -> dict:
    """POST endpoint to submit a new transaction to the mempool."""
    try:
        node_service.submit_transaction(request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"message": "Transacción añadida a la mempool"}


@app.get("/mine")
def mine() -> dict:
    """GET endpoint to trigger mining of unconfirmed transactions."""
    success = node_service.mine()
    if not success:

        return {"message": "No hay transacciones para minar"}

    latest_block = node_service.blockchain.get_latest_block()
    block_data = {
        "index": latest_block.index,
        "timestamp": latest_block.timestamp,
        "transactions": [
            {
                "sender": tx.sender,
                "recipient": tx.recipient,
                "amount": tx.amount,
                "timestamp": tx.timestamp,
                "id": tx.id,
                "signature": tx.signature,
            }
            for tx in latest_block.transactions
        ],
        "previous_hash": latest_block.previous_hash,
        "nonce": latest_block.nonce,
        "hash": latest_block.hash,
    }
    return {
        "message": "Nuevo bloque minado con éxito",
        "block": block_data,
    }


@app.get("/node/status")
def get_node_status() -> dict:
    """GET endpoint to retrieve the public key, balance, and mempool length
    of the node.
    """
    return node_service.get_node_status()


@app.post("/node/transfer")
def create_local_transfer(request: LocalTransferRequest) -> dict:
    """POST endpoint to create a local signed transfer from the node's
    resident wallet.
    """
    try:
        node_service.create_local_transfer(request.recipient, request.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"message": "Transferencia realizada con éxito y añadida a la mempool"}
