import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()


def main():
    print("Hello from langchain")

    information = """
        You are a senior software engineer. Answer with simple and practical code.  
    """

    summary_template = """
        Give me a simple Spark Scala example that reads Parquet and counts rows.
    """

    summary_prompt_template = PromptTemplate(
        input_variables=["information"], template=summary_template
    )

    llm = ChatOpenAI(
        model=os.getenv("OPENCODE_ZEN_MODEL", "minimax-m2.5-free"),
        api_key=os.environ["OPENCODE_ZEN_API_KEY"],
        base_url="https://opencode.ai/zen/v1",
        temperature=0.4,
    )

    chain = summary_prompt_template | llm

    response = chain.invoke(input={"information": information})
    print(response.content)


if __name__ == "__main__":
    main()
