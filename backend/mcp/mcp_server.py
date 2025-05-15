import asyncio

from fastmcp import FastMCP
from utils.configs import MCP_PORT, QDRANT_HOST, QDRANT_PORT, USE_CLOUD
from utils.factory import get_embedding_model
from utils.qdrant_service import QdrantService

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


# can run inspector to explore the tools using mcp dev mcp_server.py
if __name__ == "__main__":
    # mcp.run(transport="stdio")
    # mcp.run(transport="sse", host="127.0.0.1", port=9000, path="/sse")
    asyncio.run(mcp.run_streamable_http_async(host="0.0.0.0", port=MCP_PORT))
