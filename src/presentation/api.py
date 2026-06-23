from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from use_cases.node_service import NodeService

app = FastAPI(title="FabiCoin Node API")
node_service = NodeService()


class RegisterNodesRequest(BaseModel):
    nodes: List[str]


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
