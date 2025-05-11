import asyncio
from typing import Any

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

"""
Notes: Ref: https://langchain-ai.github.io/langgraph/agents/mcp/#use-mcp-tools
If MCP is a webserver
    If Transport is SSE: use http://127.0.0.1:9000/sse as url
    If Transport is streamable client, use  http://127.0.0.1:9000/mcp as url

"""


def init_llm(use_cloud_llm: bool = True):
    print("Initializing LLM..")
    if use_cloud_llm:
        print("Using cloud based LLM")
        llm = ChatOpenAI()
    else:
        llm = ChatOllama(base_url="http://localhost:7869", model="qwen3:0.6b")
    return llm


async def exec_llm_with_mcp_tools(query: str, llm: Any = None):
    if not llm:
        raise Exception("No LLM provided!")
    agent = None
    # msg = {
    #     "messages": [
    #         {
    #             "role": "user",
    #             "content": "what is the the notes content for - my secret note",
    #         }
    #     ]
    # }
    print("Creating an agent with MCP tools..")
    async with streamablehttp_client(url="http://127.0.0.1:9000/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(
            read_stream=read_stream, write_stream=write_stream
        ) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(
                llm, tools=tools
            )  # alternative for creating an agent each time is use use 1 agent that uses the same session each time (where we control the __aenter__ and __aexit__ of the streamable HTTP client)
            async for event in agent.astream({"messages": query}):
                print(event)
    return agent


if __name__ == "__main__":
    llm = init_llm()
    agent = asyncio.run(
        exec_llm_with_mcp_tools(query="Whats the email content?", llm=llm)
    )
