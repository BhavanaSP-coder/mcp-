from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Research Assistant")
DOCUMENT_PATH = Path(__file__).parent / "documents" / "research.txt"


@mcp.tool()
def search_document(query: str) -> str:
    """Search the project's research document for a topic or phrase."""
    content = DOCUMENT_PATH.read_text(encoding="utf-8")
    if query.strip().lower() in content.lower():
        return f"Information found for '{query}':\n\n{content}"
    return f"No exact match found for '{query}'. Document contents:\n\n{content}"


if __name__ == "__main__":
    mcp.run()
