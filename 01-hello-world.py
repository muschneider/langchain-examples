import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENCODE_ZEN_MODEL", "minimax-m2.5-free"),
    api_key=os.environ["OPENCODE_ZEN_API_KEY"],
    base_url="https://opencode.ai/zen/v1",
    temperature=0.2,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior software engineer. Answer with simple and practical code.",
        ),
        ("human", "{question}"),
    ]
)

chain = prompt | llm | StrOutputParser()

response = chain.invoke(
    {
        "question": "Give me a simple Spark Scala example that reads Parquet and counts rows."
    }
)

print(response)
