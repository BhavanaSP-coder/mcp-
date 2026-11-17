import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).parent
# Prefer the project's explicit credentials over an empty/stale shell variable.
load_dotenv(ROOT / ".env", override=True)


def tool_schema(tool) -> dict:
    """Convert an MCP tool definition to OpenAI's function-tool format."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


async def answer_question(question: str) -> None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise RuntimeError("Set GROQ_API_KEY in the project's .env file first.")

    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    # Use the same Python executable as this client so the active venv is respected.
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "mcp_server.py")],
    )
    client = AsyncGroq(api_key=api_key)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tools = [tool_schema(tool) for tool in tools_result.tools]
            print("MCP connection successful!")
            print("Available tools:", ", ".join(tool.name for tool in tools_result.tools))

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Answer questions using the research document when relevant. "
                        "Use search_document to retrieve evidence before answering. "
                        "If the document does not contain the answer, say so clearly."
                    ),
                },
                {"role": "user", "content": question},
            ]
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message
            messages.append(assistant_message.model_dump(exclude_none=True))

            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments or "{}")
                    print(f"\nAPI requested tool: {name}({arguments})")
                    result = await session.call_tool(name, arguments=arguments)
                    tool_output = "\n".join(
                        item.text for item in result.content if hasattr(item, "text")
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_output,
                        }
                    )

                final = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                )
                print("\nAnswer:\n" + (final.choices[0].message.content or ""))
            else:
                print("\nAnswer:\n" + (assistant_message.content or ""))

    await client.close()


async def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = input("Ask a question about the research document: ").strip()
    if not question:
        raise SystemExit("Please enter a question.")
    await answer_question(question)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from exc
