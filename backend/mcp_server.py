from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MCP_PersonalData")

# can add a context to create DB connections - say like FAISS
# ref: https://medium.com/@diwakarkumar_18755/understanding-model-context-protocol-mcp-with-langgraph-and-ollama-a-practical-guide-1aea1c2a9937


@mcp.tool()
def search_watsapp(query: str, start_time: str, end_time: str):
    "Search personal messages that are relevant to the query which are between start and end times"
    return "Hello, whats the update on the development?"


@mcp.tool()
def search_notes(query: str):
    "Search personal notes for information that are relevant to the query"
    return "1. ADD REPO TO GIT 2. CONFIGURE UV 3. HLD of the project"


@mcp.tool()
def search_email(query: str):
    "Search personal email for information that are relevant to the query"
    return "Email: From: xyz@fmail.com Subject: Very Critical issue!"


if __name__ == "__main__":
    mcp.run(transport="stdio")
