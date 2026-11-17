# MCP Research Assistant (Groq API version)

A beginner-friendly project based on the supplied guide. It preserves the Python MCP client/server and document-search flow, while replacing Ollama with Groq's API. The Groq model can request the MCP `search_document` tool, receive the document result, and write a grounded answer.

## Project layout

```text
MCP_Research_Assistant_API/
├── .env.example
├── .gitignore
├── client.py
├── mcp_server.py
├── requirements.txt
└── documents/
    └── research.txt
```

## Setup

1. Install Python 3.10 or newer.
2. In a terminal, move into this folder and create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate it:

   - Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`

4. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and set `GROQ_API_KEY` to your Groq API key. `GROQ_MODEL` defaults to `openai/gpt-oss-120b`; change it to a tool-calling model available to your Groq account if needed.
6. Ask a question:

   ```bash
   python client.py "What is Deep Learning?"
   ```

   Or run `python client.py` and enter a question when prompted.

## How it works

1. `client.py` starts `mcp_server.py` over stdio and initializes an MCP session.
2. The client lists the tools offered by the server and converts their schemas to Groq function tools.
3. The Groq API decides whether to call `search_document`.
4. If requested, the MCP client invokes the tool and returns its result to the API.
5. The API produces the final answer.

## API key safety

Keep the key only in `.env`. The `.gitignore` excludes that file from Git. Never commit or share a real key. If a key is exposed, revoke it and create a replacement. API usage may incur charges according to your provider's current pricing and account settings.

## Notes

- The MCP dependency is constrained to version 1.x to match the guide's `FastMCP` API.
- This starter uses simple substring matching, not embeddings or semantic/vector search.
- The model name is configurable through `GROQ_MODEL`; availability depends on your Groq account. The default is `openai/gpt-oss-120b`.
