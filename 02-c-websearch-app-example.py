# https://docs.langchain.com/oss/python/langchain/agents
# https://docs.langchain.com/oss/python/langchain/tools
# https://github.com/muschneider/websearch_and_crawler_app

import os
import json

# from typing import List, Dict, Any
import httpx

from dotenv import load_dotenv
from langchain_core import messages
from pydantic import BaseModel, Field

from typing import Literal

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


load_dotenv()


WEBSEARCH_API_BASE_URL = "http://127.0.0.1:8000/api/v1"


class WebSearchInput(BaseModel):
    query: str = Field(..., description="Search query to discover relevant pages.")
    max_results: int = Field(default=3, ge=1, le=10)
    provider: Literal["brave", "duckduckgo"] = Field(default="brave")


class WebExtractInput(BaseModel):
    url: str = Field(
        ..., description="Absolute http(s) URL selected from search results."
    )
    wait_for_selector: str | None = Field(
        default=None,
        description="Optional CSS selector to wait for before extracting content.",
    )
    include_links: bool = Field(default=False)


def _post_json(path: str, payload: dict, timeout: float) -> dict:
    response = httpx.post(
        f"{WEBSEARCH_API_BASE_URL}{path}",
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


# def web_search(query: str, max_results: int = 3, provider: str = "brave") -> str:
@tool(args_schema=WebSearchInput)
def web_search(query: str, max_results: int = 3, provider: str = "duckduckgo") -> str:
    """Use this tool first when the user asks a research question and you need to discover relevant web pages. It returns ranked JSON search results with title, URL, snippet, rank, and source. Do not use snippets as final evidence when the user needs source-grounded analysis; call `web_extract` on the best URLs next."""
    payload = _post_json(
        "/search",
        {
            "query": query,
            "max_results": max_results,
            "provider": provider,
        },
        timeout=30.0,
    )

    print(f"\n\n @@@>> web_search tool called - query:'{query}'")

    compact_results = [
        {
            "rank": item["rank"],
            "title": item["title"],
            "url": item["url"],
            "snippet": item.get("snippet"),
            "source": item["source"],
        }
        for item in payload["results"]
    ]

    return json.dumps(
        {
            "query": payload["query"],
            "provider": payload["provider"],
            "result_count": payload["result_count"],
            "results": compact_results,
        },
        ensure_ascii=False,
    )


@tool(args_schema=WebExtractInput)
def web_extract(
    url: str,
    wait_for_selector: str | None = None,
    include_links: bool = False,
) -> str:
    """Use this tool after `web_search` when you need to read the actual content of a selected search result URL. It returns cleaned Markdown, title, description, metadata, and final URL. Use this before summarizing, comparing, quoting, or making source-grounded claims from a page."""
    payload = _post_json(
        "/extract",
        {
            "url": url,
            "wait_for_selector": wait_for_selector,
            "include_html": False,
            "include_links": include_links,
        },
        timeout=60.0,
    )
    markdown = payload.get("markdown", "")
    max_markdown_chars = 5000

    print(f"\n\n --->> web_extract tool called - url: '{url}'")

    return json.dumps(
        {
            "url": payload["url"],
            "final_url": payload["final_url"],
            "status_code": payload["status_code"],
            "title": payload.get("title"),
            "description": payload.get("description"),
            "markdown": markdown[:max_markdown_chars],
            "truncated": len(markdown) > max_markdown_chars,
            "links": payload.get("links", [])[:10],
            "metadata": payload.get("metadata", {}),
        },
        ensure_ascii=False,
    )


def main() -> None:
    llm = ChatOpenAI(
        model=os.getenv("OPENCODE_ZEN_MODEL", "minimax-m2.5-free"),
        api_key=os.environ["OPENCODE_ZEN_API_KEY"],
        base_url="https://opencode.ai/zen/v1",
        temperature=0.4,
    )
    # llm = ChatOpenAI(
    #     model="google/gemma-4-31b-it:free",
    #     api_key=os.environ["OPENROUTER_API_KEY"],
    #     base_url="https://openrouter.ai/api/v1",
    #     temperature=0.4,
    # )

    tools = [web_search, web_extract]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a source-grounded research assistant. For research "
            "questions, you must call web_search first to discover URLs. "
            "Then call web_extract on the best one or two URLs from the "
            "search results before answering. Do not answer from search "
            "snippets alone. Cite the extracted source URLs in the final "
            "answer and mention if extracted content was truncated.",
        ),
    )

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Use web_search to find pages about MetricStore. "
                        "Then use web_extract on the top 2 useful URLs and explain when "
                        "and how MetricStore should be used. Cite URLs."
                    ),
                }
            ]
        }
    )

    # print(response["messages"])
    print("\n\n")
    print(response["messages"][-1].content)


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    main()
