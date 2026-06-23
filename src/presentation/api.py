from fastapi import FastAPI

from use_cases.node_service import NodeService

app = FastAPI(title="FabiCoin Node API")
node_service = NodeService()


@app.get("/chain")
def get_chain() -> dict:
    """GET endpoint to retrieve the complete blockchain."""
    chain_data = node_service.get_chain()
    return {"length": len(chain_data), "chain": chain_data}
