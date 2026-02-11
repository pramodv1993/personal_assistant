import asyncio

from fastmcp import FastMCP
import uvicorn
from fastapi import FastAPI
from utils.configs import MCP_PORT, QDRANT_HOST, QDRANT_PORT, USE_CLOUD
from utils.factory import get_embedding_model
from utils.qdrant_service import QdrantService
from contextlib import asynccontextmanager

mcp = FastMCP("MCP_PersonalData")
qdrant_service = QdrantService(
    host=f"{QDRANT_HOST}:{QDRANT_PORT}", create_default_collection=False
)


@mcp.tool()
async def search_data(query: str):
    "Search user history to relevant information"
    data = qdrant_service.get_similar_docs(
        query,
        embedding_func=get_embedding_model(USE_CLOUD).embed_documents,
        collection_name="test",
    )
    return "\n\n".join([doc.payload["text"] for doc in data])


mcp_app = mcp.http_app("/mcp/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Yield to the MCP lifespan manager
    async with mcp_app.lifespan(app):
        yield


mcp = FastMCP(name="Test MCP server", log_level="DEBUG")


app = FastAPI(lifespan=lifespan)


@app.get("/health_check")
def health_check():
    return {"status": "OK from MCP server"}


app.mount("/", mcp_app)


# can run inspector to explore the tools using mcp dev mcp_server.py
if __name__ == "__main__":
    # mcp.run(transport="stdio")
    # mcp.run(transport="sse", host="127.0.0.1", port=9000, path="/sse")
    uvicorn.run(app, host="0.0.0.0", port=MCP_PORT)
