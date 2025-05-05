# generating synthetic messages, emails, notes
from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class Message(BaseModel):
    messages: List[str] = Field(description="List of 20 messages")


op_parser = PydanticOutputParser(pydantic_object=Message)
openai_gpt = ChatOpenAI(model="gpt-3.5-turbo-0125")


def dump_res(data, op_path: str):
    f = open(op_path, "w")
    f.writelines(data)
    f.close()


def generate_chat_samples():
    print("Generating chat samples")
    chat_prompt = """You are an expert in generating synthetic data. Your task is to generate 20 samples of chat messages.
    Follow the below guidelines:
    1. Return a list of strings under the key 'messages'
    2. Follow the format dd/mm/yyyy, HH:MM:ss AM/PM: <Random User Name>: <Random Message> while generating each sample
    3. Ensure the 20 messages are in the context of a topic in a software firm
    4. There could me multiple messages on the same day as part of a conversation
    4. Format instructions: {format}"""
    prompt = PromptTemplate.from_template(
        template=chat_prompt,
        partial_variables={"format": op_parser.get_format_instructions()},
    )
    chain = prompt | openai_gpt | op_parser
    chat_messages = chain.invoke(input={})
    dump_res("\n".join(chat_messages.messages), "data/sample_chats.txt")


def generate_email_samples():
    print("Generating email samples")
    email_prompt = """You are an expert in generating synthetic data. Your task is to generate 20 samples of email messages.
    Follow the below guidelines:
    1. Return a list of strings under the key 'messages'
    2. Ensure the sample messages follow the actual format of an email from a provider such as Gmail
    3. Also some samples can have multiple conversation threads
    4. Ensure the emails are not just boilerplate, but dense and filled with details, they may contain 2-4 paragraphs as well.
    4. Come up with dummy names, include timestamps, signatures, MIME headers etc
    5. Ensure the 20 messages are in the context of a topic in a software firm
    6. Format instructions: {format}"""
    prompt = PromptTemplate.from_template(
        template=email_prompt,
        partial_variables={"format": op_parser.get_format_instructions()},
    )
    chain = prompt | openai_gpt | op_parser
    chat_messages = chain.invoke(input={})
    dump_res(
        "---------------------".join(chat_messages.messages), "data/sample_emails.txt"
    )


def generate_note_samples():
    print("Generating notes, memos samples")
    notes_prompt = """You are an expert in generating synthetic data. Your task is to generate 20 samples of personal memos, notes, checklists from a personal diary.
    Follow the below guidelines:
    1. Return a list of strings under the key 'messages'
    2. Ensure the 20 messages are in the context of a topic in a software firm
    4. Format instructions: {format}"""
    prompt = PromptTemplate.from_template(
        template=notes_prompt,
        partial_variables={"format": op_parser.get_format_instructions()},
    )
    chain = prompt | openai_gpt | op_parser
    chat_messages = chain.invoke(input={})
    dump_res("\n".join(chat_messages.messages), "data/sample_notes.txt")


if __name__ == "__main__":
    generate_chat_samples()
    generate_email_samples()
    generate_note_samples()
