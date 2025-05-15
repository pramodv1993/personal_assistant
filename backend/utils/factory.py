from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from utils.configs import (
    OLLAMA_EMBEDDING,
    OLLAMA_HOST,
    OLLAMA_LLM,
    OLLAMA_LOCAL_HOST,
    OLLAMA_LOCAL_PORT,
    OLLAMA_PORT,
    OPENAI_EMBEDDING,
    OPENAI_KEY,
    OPENAI_LLM,
)

embedding_models = {"cloud": {}, "ollama": {}}


def _get_ollama_url(within_container: bool = True):
    return (
        f"{OLLAMA_HOST}:{OLLAMA_PORT}"
        if within_container
        else f"{OLLAMA_LOCAL_HOST}:{OLLAMA_LOCAL_PORT}"
    )


def get_embedding_model(cloud: bool = True, within_container: bool = True):
    return (
        OpenAIEmbeddings(model=OPENAI_EMBEDDING, api_key=OPENAI_KEY)
        if cloud
        else OllamaEmbeddings(
            model=OLLAMA_EMBEDDING,
            base_url=_get_ollama_url(within_container=within_container),
        )
    )


def get_llm(cloud: bool = True, within_container: bool = True):
    return (
        ChatOpenAI(model=OPENAI_LLM, api_key=OPENAI_KEY)
        if cloud
        else ChatOllama(
            base_url=_get_ollama_url(within_container=within_container),
            model=OLLAMA_LLM,
        )
    )
