import asyncio
import contextlib
from typing import Any, Literal

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client


def init_llm(use_cloud_llm: bool = True):
    print("Initializing LLM..")
    if use_cloud_llm:
        print("Using cloud based LLM")
        llm = ChatOpenAI()
    else:
        llm = ChatOllama(base_url="http://localhost:7869", model="qwen3:0.6b")
    return llm


@contextlib.asynccontextmanager
async def connect_to_mcp_server(
    mcp_host: str = "http://localhost",
    mcp_port: int = 9000,
    transport: Literal["streamable_http", "sse"] = "streamable_http",
):
    url = f"{mcp_host}:{mcp_port}"
    if transport == "sse":
        url += "/sse"
        async with sse_client(url) as (read_stream, write_stream):
            async with ClientSession(
                read_stream=read_stream, write_stream=write_stream
            ) as session:
                await session.initialize()
                yield session
    else:
        url += "/mcp"
        async with streamablehttp_client(url) as (read_stream, write_stream, _):
            async with ClientSession(
                read_stream=read_stream, write_stream=write_stream
            ) as session:
                await session.initialize()
                yield session


async def exec_llm_with_mcp_tools(
    query: str,
    llm: Any = None,
    mcp_host: str = "http://127.0.0.1",
    mcp_port: int = 9000,
):
    if not llm:
        raise Exception("No LLM provided!")
    agent = None
    print("Creating an agent with MCP tools..")
    async with connect_to_mcp_server(
        transport="streamable_http", mcp_host=mcp_host, mcp_port=mcp_port
    ) as session:
        await session.initialize()
        tools = await load_mcp_tools(session)
        # if same agent needs to reused, then explicitly control the __aenter__ and __aexit__ methods of the session's context manager
        agent = create_react_agent(llm, tools=tools)
        async for event in agent.astream({"messages": query}):
            print(event)
    return agent


if __name__ == "__main__":
    llm = init_llm()
    agent = asyncio.run(
        exec_llm_with_mcp_tools(
            query="summarize email from Lauren??",
            llm=llm,
            mcp_host="http://127.0.0.1",
            mcp_port=9000,
        )
    )
