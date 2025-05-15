from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from mcp_utils import exec_llm_with_mcp_tools
from utils.configs import MCP_HOST, MCP_PORT, USE_CLOUD
from utils.factory import get_llm

app = FastAPI()
llm = get_llm(USE_CLOUD)


@app.get("/health_check")
async def read_root():
    return {"status": "OK"}


@app.post("/ask_ai")
async def execute_query(query: str):
    return StreamingResponse(
        exec_llm_with_mcp_tools(
            query=query, llm=llm, mcp_host=MCP_HOST, mcp_port=MCP_PORT
        )
    )
