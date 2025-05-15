QDRANT_HOST = "http://qdrant"
QDRANT_LOCAL_HOST = "http://localhost"
QDRANT_PORT = 6333
MCP_HOST = "http://mcp"
MCP_PORT = 9000
OLLAMA_HOST = "http://ollama"
OLLAMA_PORT = 11434
OLLAMA_LOCAL_HOST = "http://localhost"
OLLAMA_LOCAL_PORT = 11434
OLLAMA_LLM = "qwen3:0.6b"
OLLAMA_EMBEDDING = "nomic-embed-text"

OPENAI_KEY = ""
OPENAI_LLM = "gpt-3.5-turbo-0125"
OPENAI_EMBEDDING = "text-embedding-3-small"


USE_CLOUD = False
EMBEDDING_DIM = 768 if not USE_CLOUD else 1536
