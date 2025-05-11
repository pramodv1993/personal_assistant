import asyncio

from fastmcp import FastMCP

mcp = FastMCP("MCP_PersonalData")


@mcp.tool()
async def search_watsapp(query: str, start_time: str, end_time: str):
    "Search personal messages that are relevant to the query which are between start and end times"
    return "Hello, whats the update on the development?"


@mcp.tool()
async def search_notes(query: str):
    "Search personal notes for information that are relevant to the query"
    return f"Response to query {query}: 1. ADD REPO TO GIT 2. CONFIGURE UV 3. HLD of the project"


@mcp.tool()
async def search_email(query: str):
    "Search personal email for information that are relevant to the query"
    return "Email: From: xyz@fmail.com Subject: Very Critical issue!"


# can run inspector to explore the tools uysing
if __name__ == "__main__":
    # mcp.run(transport="stdio")
    # mcp.run(transport="sse", host="127.0.0.1", port=9000, path="/sse")
    asyncio.run(mcp.run_streamable_http_async(host="127.0.0.1", port=9000, path="/mcp"))
