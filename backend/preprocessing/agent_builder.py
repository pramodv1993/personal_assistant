# Doc processing agent
"""
Identify the doc type and invoke the respective processing + ingestion tool
"""

import os
import re
from itertools import chain
from typing import Annotated
from uuid import uuid4

import pandas as pd
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from tenacity import retry, stop_after_attempt
from typing_extensions import TypedDict
from utils.qdrant_service import QdrantClient


class State(TypedDict):
    messages: Annotated[list, add_messages]


@tool
@retry(stop=stop_after_attempt(3))
def process_chats(file_path: str):
    """Process chat contents"""

    def message_formatter(date, msgs):
        chats = f"(Date: {date}) "
        for user, msg in msgs:
            chats += f"{user}: {msg}\n\n"
        return chats

    qdrant.create_collection("test", 1536, recreate=False)
    if not os.path.exists(file_path):
        return FileNotFoundError("File not found!")
    print(f"Using `process_chats` tool for the file {file_path}")
    data = open(file_path, "r").read()
    messages = re.findall(
        "(\d{1,2}/\d{1,2}/\d{1,4}, \d{1,2}:\d{1,2}:\d{1,2} [AP]M): (.*):(.*)", data
    )
    system_messages = [
        "image omitted",
        "video omitted",
        "you were added",
        "created this group",
    ]
    messages = [
        (date, user.lower().strip(), msg.lower().strip())
        for date, user, msg in messages
        if not any([sys_msg in msg.lower() for sys_msg in system_messages])
    ]
    df = pd.DataFrame.from_records(messages, columns=["date", "user", "message"])
    df["date"] = pd.to_datetime(df.date, format="%d/%m/%Y, %I:%M:%S %p")
    df["date_str"] = df["date"].dt.strftime("%d-%m-%Y")
    df = df.groupby([df.date_str])[["user", "message"]].apply(
        lambda x: list(zip(x["user"], x["message"]))
    )
    formatted_chats = (
        df.reset_index()
        .apply(lambda x: message_formatter(x["date_str"], x[0]), axis=1)
        .to_list()
    )
    # @TODO add chunker at some point
    print("Formatted chats..")
    qdrant.insert_docs(
        "test",
        formatted_chats,
        metadatas=[{"doc_type": "chat"}] * len(formatted_chats),
        include_doc_in_payload=True,
        embedding_func=openai_embedding.embed_documents,
    )
    print("Inserted chats to vec store")
    return {"messages": ["Processing Done"]}


@tool
@retry(stop=stop_after_attempt(3))
def process_emails(file_path: str):
    """Process email contents"""
    if not os.path.exists(file_path):
        return FileNotFoundError("File not found!")
    print(f"Using `process_emails` tool for the file {file_path}")
    qdrant.create_collection("test", 1536, recreate=False)
    data = open(file_path, "r").read().split("---------------------")
    # mask PIIs
    emails = [
        re.sub(r"[a-zA-Z0-9%._\-\+]+@\w+\.\w+", "####", mail).strip().lower()
        for mail in data
    ]
    # identify each email uniquely before chunking them
    email_no_vs_chunked_emails = [
        (uuid4().hex, text_splitter.split_text(email)) for email in emails
    ]
    # update the email no. for metadata to retrieve all the related chunks pertaining to an email
    metadatas = [
        {"chunk_no": i + 1, "doc_type": "email", "email_no": email_no}
        for email_no, chunks in email_no_vs_chunked_emails
        for i, _ in enumerate(chunks)
    ]
    # post processing after chunking
    chunked_emails = [
        chunk.strip()
        for chunk in list(
            chain(*[chunked_emails for _, chunked_emails in email_no_vs_chunked_emails])
        )
    ]
    print("Processed Emails")
    qdrant.insert_docs(
        "test",
        chunked_emails,
        embedding_func=openai_embedding.embed_documents,
        metadatas=metadatas,
        include_doc_in_payload=True,
    )
    print("Inserted in Vector store")


@tool
@retry(stop=stop_after_attempt(3))
def process_notes(file_path: str):
    """Process notes, personal memos etc"""
    qdrant.create_collection("test", 1536, recreate=False)
    if not os.path.exists(file_path):
        return FileNotFoundError("File not found!")
    print(f"Using `process_notes` tool for the file {file_path}")
    data = open(file_path, "r").read()
    chunked_texts = text_splitter.split_text(data)
    print("Chunked documents..")
    qdrant.insert_docs(
        collection_name="test",
        docs=chunked_texts,
        embedding_func=openai_embedding.embed_documents,
        metadatas=[{"doc_type": "note"}] * len(chunked_texts),
        include_doc_in_payload=True,
    )
    print("Inserted chunked documents")
    return {"messages": ["Processing Done"]}


def doc_processor(state: State):
    prompt = """You are a document processing assistant. Given a file snippet, carefully analyze the content and select exactly ONE tool that best describes the snippet to processs the document.
    Available tools and their associated tools:
    - `process_chats` to process chat messages
    - `process_emails` to process email content
    - `process_notes` to process notes, memos, code etc

    ONLY select one tool that best fits the content. Do not call more than one.
    You HAVE to choose one tool.
    """
    response = openai_gpt_with_tools.invoke(
        [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"Given the snippet: {state['messages'][0].content}",
            },
        ]
    )
    return {"messages": [response]}


def node_router(state: State):
    if isinstance(state, list):
        last_message = state[-1]
    elif messages := state.get("messages", []):
        last_message = messages[-1]
    else:
        raise ValueError(f"No messages found in state : {state}")
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tool_executor"
    return END


def post_process(output: str):
    return output.split("\n\n")[-1]


llm = ChatOllama(
    base_url="http://localhost:7869", model="qwen3:0.6b"
)  # sel-hosted model
openai_gpt = ChatOpenAI(model="gpt-3.5-turbo-0125")
openai_embedding = OpenAIEmbeddings(
    model="text-embedding-3-small"
)  # @ TODO change to self hosted embedding model
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400, chunk_overlap=100, length_function=len, is_separator_regex=False
)
qdrant = QdrantClient()
tools = [process_chats, process_emails, process_notes]
openai_gpt_with_tools = openai_gpt.bind_tools(tools, tool_choice="required")
llm_with_tools = llm.bind_tools(tools, tool_choice="required")


def construct_data_processing_graph():
    tool_node = ToolNode(tools)
    graph_builder = StateGraph(State)
    graph_builder.add_node("doc_processor", doc_processor)
    graph_builder.add_node("tool_executor", tool_node)

    graph_builder.add_edge(START, "doc_processor")
    graph_builder.add_conditional_edges(
        "doc_processor", node_router, {"tool_executor": "tool_executor", END: END}
    )

    graph = graph_builder.compile()
    graph.get_graph().print_ascii()
    return graph
