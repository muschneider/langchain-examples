# https://docs.langchain.com/oss/python/langchain/agents
# https://docs.langchain.com/oss/python/langchain/tools

import os
import json
from typing import List, Dict, Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


load_dotenv()


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class SearchInput(BaseModel):
    query: str = Field(description="Search query to execute on the web")
    max_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of search results to return",
    )


def playwright_duckduckgo_search(
    query: str, max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search DuckDuckGo using Playwright and return organic results.

    This uses DuckDuckGo's HTML endpoint because it is simpler and more stable
    than heavily JavaScript-rendered search pages.
    """

    results: List[Dict[str, Any]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )

        page = context.new_page()

        try:
            page.goto(
                "https://duckduckgo.com/html/",
                wait_until="domcontentloaded",
                timeout=30000,
            )

            page.fill("input[name='q']", query)
            page.press("input[name='q']", "Enter")

            page.wait_for_selector(".result", timeout=15000)

            items = page.locator(".result")
            count = min(items.count(), max_results)

            for i in range(count):
                item = items.nth(i)

                title_locator = item.locator(".result__title")
                link_locator = item.locator(".result__a")
                snippet_locator = item.locator(".result__snippet")

                title = title_locator.inner_text(timeout=5000).strip()

                url = ""
                if link_locator.count() > 0:
                    url = link_locator.first.get_attribute("href") or ""

                snippet = ""
                if snippet_locator.count() > 0:
                    snippet = snippet_locator.first.inner_text(timeout=5000).strip()

                if title and url:
                    results.append(
                        {
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                        }
                    )

        except PlaywrightTimeoutError:
            results.append(
                {
                    "title": "Search timeout",
                    "url": "",
                    "snippet": f"Search timed out for query: {query}",
                }
            )
        finally:
            context.close()
            browser.close()

    return results


@tool("web_search_with_playwright", args_schema=SearchInput)
def web_search_with_playwright(query: str, max_results: int = 5) -> str:
    """
    Search the web using Playwright and return search results.

    Use this tool when the user asks for recent information, URLs,
    documentation, examples, comparisons, or anything that may require
    current web search.
    """
    results = playwright_duckduckgo_search(query=query, max_results=max_results)

    return json.dumps(results, indent=2, ensure_ascii=False)


def main() -> None:
    # llm = ChatOpenAI(
    #    model="openai/gpt-oss-120b:free",
    #    api_key=os.environ["OPENROUTER_API_KEY"],
    #    base_url="https://openrouter.ai/api/v1",
    #    temperature=0,
    # )
    llm = ChatOpenAI(
        model=os.getenv("OPENCODE_ZEN_MODEL", "minimax-m2.5-free"),
        api_key=os.environ["OPENCODE_ZEN_API_KEY"],
        base_url="https://opencode.ai/zen/v1",
        temperature=0.4,
    )

    agent = create_agent(
        model=llm,
        tools=[web_search_with_playwright],
        system_prompt=(
            "You are a technical research assistant. "
            "When you need current or external information, use the Playwright search tool. "
            "Always summarize results clearly and include URLs when available."
        ),
    )

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "search for job postings for an ai engineer using langchain on linkedin and list their details. "
                    ),
                }
            ]
        }
    )

    print(response["messages"][-1].content)


if __name__ == "__main__":
    main()
