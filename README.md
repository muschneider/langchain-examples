# LangChain Course

A small Python learning project for experimenting with LangChain agents, OpenAI-compatible chat models, Playwright-powered web search, and Tavily search. The repository contains standalone examples rather than a packaged application, so each script can be run independently while following the course exercises.

## Tech Stack

| Area                | Technology                  |
| ------------------- | --------------------------- |
| Language            | Python 3.12+                |
| Package management  | uv                          |
| Environment loading | python-dotenv / dotenv      |
| LLM integration     | LangChain, langchain-openai |
| Search tools        | Playwright, Tavily          |
| Validation          | Pydantic                    |
| Linting             | Ruff                        |
| Tool versioning     | mise, optional              |

## Prerequisites

- Python 3.12 or newer.
- `uv` for dependency management.
- API keys for the examples you want to run.
- Chromium browser dependencies for the Playwright example.

If you use `mise`, this repository includes `mise.toml` to install `uv` and auto-activate `.venv` when entering the directory.

## Setup

### 1. Install Dependencies

```bash
uv sync
```

This creates `.venv` and installs the runtime and development dependencies from `pyproject.toml` and `uv.lock`.

### 2. Install Playwright Browser

The Playwright search example launches Chromium, so install the browser once:

```bash
uv run playwright install chromium
```

On a fresh Linux machine, Playwright may also require system packages:

```bash
uv run playwright install-deps chromium
```

### 3. Configure Environment Variables

Create a local `.env` file in the project root:

```bash
touch .env
```

Add only the keys needed by the scripts you plan to run:

```bash
# Required by 01-hello-world.py and 02-b-websearch-tavily-example.py
OPENROUTER_API_KEY=your_openrouter_api_key

# Required by 02-a-websearch-playwright-example.py
OPENCODE_ZEN_API_KEY=your_opencode_zen_api_key

# Optional override for 02-a-websearch-playwright-example.py
OPENCODE_ZEN_MODEL=minimax-m2.5-free

# Required by 02-b-websearch-tavily-example.py
TAVILY_API_KEY=your_tavily_api_key
```

The `.env` file is ignored by git and should not be committed.

## Running The Examples

### Basic LangChain Chat Example

```bash
uv run python 01-hello-world.py
```

This script loads environment variables, creates a `PromptTemplate`, connects it to an OpenRouter-backed `ChatOpenAI` model, invokes the chain, and prints the model response.

### Playwright Web Search Agent

```bash
uv run python 02-a-websearch-playwright-example.py
```

This script defines a custom LangChain tool named `web_search_with_playwright`. The tool opens DuckDuckGo's HTML search page with Playwright, extracts result titles, URLs, and snippets, then passes those results back to the agent.

### Tavily Web Search Agent

```bash
uv run python 02-b-websearch-tavily-example.py
```

This script uses the built-in `TavilySearch` tool from `langchain-tavily`. It also defines Pydantic models for a structured response containing an answer and source URLs.

## Project Structure

```text
.
|-- 01-hello-world.py                    # Basic LangChain prompt and LLM chain
|-- 02-a-websearch-playwright-example.py # Agent with custom Playwright web search tool
|-- 02-b-websearch-tavily-example.py     # Agent with Tavily search and structured output
|-- pyproject.toml                       # Project metadata and dependencies
|-- uv.lock                              # Locked dependency graph
|-- mise.toml                            # Optional mise tool and venv configuration
|-- .python-version                      # Python version hint
|-- .gitignore                           # Ignored local/generated files
`-- README.md                            # Project documentation
```

## Dependencies

Runtime dependencies are declared in `pyproject.toml`:

| Dependency         | Purpose                                                                        |
| ------------------ | ------------------------------------------------------------------------------ |
| `langchain`        | Core LangChain APIs, agents, tools, and prompt composition                     |
| `langchain-openai` | OpenAI-compatible chat model integration used with OpenRouter and OpenCode Zen |
| `langchain-tavily` | LangChain integration for Tavily search                                        |
| `tavily-python`    | Tavily API client                                                              |
| `playwright`       | Browser automation for the custom DuckDuckGo search tool                       |
| `pydantic`         | Typed input and output schemas                                                 |
| `dotenv`           | Loads local `.env` variables                                                   |

Development dependencies:

| Dependency | Purpose                              |
| ---------- | ------------------------------------ |
| `ruff`     | Python linting and formatting checks |

## Useful Commands

| Command                                              | Description                       |
| ---------------------------------------------------- | --------------------------------- |
| `uv sync`                                            | Install dependencies into `.venv` |
| `uv run python 01-hello-world.py`                    | Run the basic chat example        |
| `uv run python 02-a-websearch-playwright-example.py` | Run the Playwright search agent   |
| `uv run python 02-b-websearch-tavily-example.py`     | Run the Tavily search agent       |
| `uv run playwright install chromium`                 | Install Chromium for Playwright   |
| `uv run ruff check .`                                | Run lint checks                   |
| `uv run ruff format .`                               | Format Python files               |

## Environment Variables

| Variable               | Required For                                            | Description                                           |
| ---------------------- | ------------------------------------------------------- | ----------------------------------------------------- |
| `OPENROUTER_API_KEY`   | `01-hello-world.py`, `02-b-websearch-tavily-example.py` | API key for OpenRouter's OpenAI-compatible endpoint   |
| `OPENCODE_ZEN_API_KEY` | `02-a-websearch-playwright-example.py`                  | API key for OpenCode Zen's OpenAI-compatible endpoint |
| `OPENCODE_ZEN_MODEL`   | Optional for `02-a-websearch-playwright-example.py`     | Model name override, defaults to `minimax-m2.5-free`  |
| `TAVILY_API_KEY`       | `02-b-websearch-tavily-example.py`                      | API key used by the Tavily search tool                |

## Notes For Course Work

- The examples are intentionally small and script-oriented.
- The prompts and search queries are hard-coded so they can be edited directly while experimenting.
- The LLM clients use OpenAI-compatible endpoints, so models can be swapped by changing the `model`, `api_key`, and `base_url` values in each script.
- `load_dotenv()` is called in each script, so local `.env` values are available automatically when running through `uv run`.

## Troubleshooting

### Missing API Key

If a script fails with `KeyError: 'OPENROUTER_API_KEY'`, `KeyError: 'OPENCODE_ZEN_API_KEY'`, or an authentication error, add the missing key to `.env` and run the script again.

### Playwright Browser Not Installed

If the Playwright example fails because Chromium is missing, run:

```bash
uv run playwright install chromium
```

### Playwright System Dependency Errors

On Linux, install the browser system dependencies with:

```bash
uv run playwright install-deps chromium
```

### Tavily Authentication Errors

The Tavily example relies on `TAVILY_API_KEY`. Confirm that the key exists in `.env` and that the shell command is being run from the repository root.

### Environment Not Activated

You do not need to activate `.venv` manually when using `uv run`. If you prefer manual activation, use:

```bash
source .venv/bin/activate
```

Then run scripts with plain `python`.

## License

No license file is currently included in this repository.
