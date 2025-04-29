from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama.llms import OllamaLLM
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# @ TODO add a self hosted CustomLLM and configure with langchain ollama (https://python.langchain.com/docs/integrations/llms/ollama/)
llm = OllamaLLM()


async def main():
    server_params = StdioServerParameters(command="python", args=["mcp_server.py"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            # @TODO create a langgraph based agent
            agent = create_react_agent(llm, tools)
            # @TODO parameterize the below to be invoked by the watsapp bot
            msg = {"messages": "Test query"}
            res = await agent.ainvoke(msg)
            return res
