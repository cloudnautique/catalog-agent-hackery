# server.py - MCP Discoverer using FastMCP
from fastmcp import FastMCP
from fetch_mcp_repos import fetch_repos_page, get_repo_by_id, search_repos

mcp = FastMCP(
    name="MCP Discoverer",
    description="A simple MCP server for discovering MCP resources.",
    instructions="Use this to iterate and work with MCP repository information.",
)


@mcp.tool(
    annotations={
        "title": "List MCP Repositories",
        "readOnlyHint": True,
        "openWorldHint": True,
    }
)
async def list_mcp_repos(limit: int = 100, offset: int = 0) -> list[dict]:
    """List MCP repos with name, stars, and GitHub link asynchronously."""
    repos = await fetch_repos_page(limit=limit, offset=offset)
    return [
        {
            "name": repo.get("fullName"),
            "stars": repo.get("stars"),
            "url": repo.get("url"),
            "repo_id": repo.get("id"),
        }
        for repo in repos
    ]


@mcp.tool(
    annotations={
        "title": "Search MCP Repositories",
        "description": "Search MCP repositories by query string. Returns the API URL and results.",
        "readOnlyHint": True,
        "openWorldHint": True,
    }
)
async def search_mcp_repos(query: str) -> dict:
    """Search MCP repos by query string asynchronously. Returns API URL and results."""
    return await search_repos(query)


@mcp.tool(
    annotations={
        "title": "Get MCP Repository",
        "description": "Retrieve a single MCP repository by its ID, returning complete repository information.",
        "readOnlyHint": True,
        "openWorldHint": True,
    }
)
async def get_mcp_repo_tool(repo_id: int) -> dict:
    """Get a single MCP repo by its ID asynchronously, returns complete repo info."""
    return await get_repo(repo_id)


@mcp.resource("mcp://repo/{repo_id}", mime_type="application/json")
async def get_mcp_repo(repo_id: int):
    """Get a single MCP repo by its ID asynchronously, returns complete repo info."""
    return await get_repo(repo_id)


async def get_repo(repo_id: int):
    """Helper to fetch a single MCP repo by ID asynchronously."""
    repo = await get_repo_by_id(repo_id)
    if not repo:
        return {"error": "Repository not found"}
    return repo


if __name__ == "__main__":
    mcp.run()
