# agent.py - Refactored to use GitHub Python API (PyGithub) to analyze MCP repos and output a CSV
import os
import asyncio
from agents import Agent, Runner, function_tool
from agents.mcp.server import MCPServerStdio
from csv_utils import initialize_csv, append_rows
from model import CSV_HEADERS, RepoFeatureRow, StrictMCPServerStdioParams
from github_utils import search_github_repos_with_pagination
from typing import Any

feature_agent_instructions = (
    "You are a GitHub repository feature extraction agent for Model Context Protocol (MCP) servers. "
    "Your task is to analyze GitHub repositories and extract specific information for MCP servers."
    "First use search_repositories for the specific repo to obtain the Repo object, it will have things like stars, forks, and license."
    "Next get the ENTIRE README from the repo, DO NOT TRUNCATE AT ANY POINT!"
    "Using the repo and readme data, determine if this is an MCP server, and not an MCP SDK, client, inspector, or hosting platform."
    "If it is not an MCP server, return 'Not an MCP server'in the description. Be done, Do not Continue, leave the remaining fields blank."
    "For an MCP server extract the repo url, name, description, readme, license."
    "ONLY use the README to determine if the repo runs via Docker(Y/N), UVX(Y/N), NPX(Y/N), extract the commands to run the server."
    "Determine if the MCP Server will require filesystem access(Y/N), and if it requires credentials."
    "If MCP server is run Docker, UVX, NPX server, test the mcp stdio server and return the list of tools it supports. ONLY fill in tools list if successful otherwise leave blank."
)

@function_tool(strict_mode=False)
async def test_mcp_stdio_server_tool(command: StrictMCPServerStdioParams) -> Any:
    """
    Test the command is a valid MCP server activation command.
    Returns the list of tools that the MCP server supports.

    Args:
        command: The object to start the server {"command": "uvx", "args": ["run", "--foo"], "env": {"FOO": "bar"}}
    """
    async with MCPServerStdio(
        params=command.model_dump(),
        client_session_timeout_seconds=10
    ) as server:
        return await server.list_tools()


async def agent_main(token=None, repo=None, output_csv="mcp_repos.csv"):
    try:
        await asyncio.wait_for(_agent_main_inner(token, repo, output_csv), timeout=60)
    except asyncio.TimeoutError:
        print(f"Timeout: MCP server did not respond in time for repo {repo}. Skipping.")
    except Exception as e:
        print(f"Error in agent_main for repo {repo}: {e}")

async def _agent_main_inner(token, repo, output_csv):
    async with MCPServerStdio(
        cache_tools_list=True,
        params={"command": "docker", "args":[
            "run",
            "-i",
            "--rm",
            "-e",
            "GITHUB_PERSONAL_ACCESS_TOKEN",
            "-e",
            "GITHUB_HOST",
            "ghcr.io/github/github-mcp-server"
        ], "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": token}
        },
        client_session_timeout_seconds=10
    ) as server:
        feature_agent = Agent(
            name="GitHub Repo Search Agent",
            instructions=feature_agent_instructions,
            model="gpt-4.1",
            mcp_servers=[server],
            tools=[
                test_mcp_stdio_server_tool,
            ],
            output_type=RepoFeatureRow
        )

        input = f"process the following GitHub repository: {repo}"
        print(f"Processing {input}...")

        repoFeatureRow = await Runner.run(feature_agent, input=input)
        # Extract the actual RepoFeatureRow model from the RunResult
        repo_feature_row = repoFeatureRow.final_output_as(RepoFeatureRow)
        append_rows(output_csv, [repo_feature_row], headers=CSV_HEADERS)



async def main(num_repos=5, output_csv="mcp_repos.csv", token=None):
    if not token:
        raise ValueError("GitHub token required")

    query=Agent(name="GitHub Query Generator", 
          instructions=(
              "Generate a valid GitHub API search query string for search_repositories."
              "Just the part that is the query like 'mcp in:name,description,readme model context protocol in:name,description,readme'"
              "respond with exactly the query, nothing else."
          )
    )
    query = await Runner.run(query, input="Generate a query to search GitHub repositories for Model Context Protocol (MCP) servers.")
    print(f"Query: {query.final_output_as(str)}")
    #query = 'mcp in:name,description,readme model context protocol in:name,description,readme'
    repos_iter = search_github_repos_with_pagination(token, query.final_output_as(str), max_items=num_repos)
    print(f"Processing up to {num_repos} repos.")

    initialize_csv(output_csv, CSV_HEADERS)
    count = 0
    for repo in repos_iter:
        try:
            await agent_main(token=token, repo=repo, output_csv=output_csv)
            count += 1
        except Exception as e:
            print(f"Error processing repo {repo}: {e}")
            continue
    print(f"Wrote {count} rows to {output_csv}")
    await asyncio.sleep(0.1)  # Give asyncio a moment to clean up subprocesses


if __name__ == "__main__":
    GH_TOKEN = os.getenv("GH_TOKEN")
    asyncio.run(main(num_repos=100, token=GH_TOKEN))