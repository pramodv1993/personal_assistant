import contextlib
from typing import Any, Literal

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from utils.configs import (
    MCP_HOST,
    MCP_PORT,
)


@contextlib.asynccontextmanager
async def connect_to_mcp_server(
    mcp_host: str = MCP_HOST,
    mcp_port: int = MCP_PORT,
    transport: Literal["streamable_http", "sse"] = "streamable_http",
):
    url = f"{mcp_host}:{mcp_port}"
    if transport == "sse":
        url += "/sse"
        print(f"MCP URL: {url}")
        async with sse_client(url) as (read_stream, write_stream):
            async with ClientSession(
                read_stream=read_stream, write_stream=write_stream
            ) as session:
                await session.initialize()
                yield session
    else:
        url += "/mcp"
        print(f"MCP URL: {url}")
        async with streamablehttp_client(url) as (read_stream, write_stream, _):
            async with ClientSession(
                read_stream=read_stream, write_stream=write_stream
            ) as session:
                await session.initialize()
                yield session


async def exec_llm_with_mcp_tools(
    query: str,
    llm: Any = None,
    mcp_host: str = MCP_HOST,
    mcp_port: int = MCP_PORT,
):
    if not llm:
        raise Exception("No LLM provided!")
    agent = None
    print("Creating an agent with MCP tools..")
    async with connect_to_mcp_server(
        transport="streamable_http", mcp_host=mcp_host, mcp_port=mcp_port
    ) as session:
        tools = await load_mcp_tools(session)
        # if same agent needs to reused, then explicitly control the __aenter__ and __aexit__ methods of the session's context manager
        prompt = """You are a helpful chat bot assistant. Given a user query and responses from tools, your task is to summarize the tool responses and address the user query."""
        agent = create_react_agent(llm, tools=tools, prompt=prompt)
        async for chunk, _ in agent.astream(
            {"messages": query}, stream_mode="messages"
        ):
            if chunk.content and not hasattr(chunk, "tool_call_id"):
                yield chunk.content
