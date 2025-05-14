# agent.py - OpenAI agent SDK app to analyze MCP repos and output a CSV using the OpenAI Agents SDK
import asyncio
import json
from pydantic import BaseModel

from agents import Agent, Runner, function_tool, ModelSettings
from fetch_mcp_repos import process_all_repos
from agents.mcp.server import MCPServerStdio
from csv_utils import initialize_csv, append_rows

CSV_HEADERS = [
    "Repo Name",
    "Docker",
    "UVX",
    "NPX",
    "Filesystem Access",
    "Credentials",
    "Example Activation Command(s)",
]


class RepoFeatureRow(BaseModel):
    repo_name: str
    docker: str
    uvx: str
    npx: str
    filesystem_access: str
    credentials: str
    example_activation_commands: str


class FeatureExtractionOutput(BaseModel):
    repo_name: str
    docker: str
    uvx: str
    npx: str
    filesystem_access: str
    credentials: str
    example_activation_commands: str


feature_extraction_instructions = (
    "You will be given a JSON object with keys: 'repo_id' (the MCP repo ID), and 'output_csv' (CSV path)."
    " First, fetch full repository details by calling get_mcp_repo_tool(repo_id)."
    " Then extract the following features from the repo dict:"
    " repo_name (fullName), docker support (yes/no), uvx support (yes/no), npx support (yes/no), filesystem_access (yes/no), credentials (if any), example_activation_commands (if any, keep raw and one per line if more then one)."
    " Finally, invoke append_rows(output_csv, [[repo_name, docker, uvx, npx, filesystem_access, credentials, example_activation_commands]])."
    " Use only tool calls for side effects and return no extra text."
)


async def main(num_repos=20, output_csv="mcp_repos.csv"):
    # Step 0: start the MCP server and keep it open
    async with MCPServerStdio(
        params={"command": "python", "args": ["server.py"]},
        name="Local MCP Server (stdio)",
    ) as mcp_server:
        # Initialize output CSV with headers before agent runs
        initialize_csv(output_csv, CSV_HEADERS)

        # Create the feature extraction agent
        feature_agent = Agent(
            name="MCP Repo Feature Extractor",
            instructions=feature_extraction_instructions,
            model="gpt-4.1",
            model_settings=ModelSettings(tool_choice="auto"),
            tools=[append_rows],
            mcp_servers=[mcp_server],
        )

        # Define a page handler to process each page of repos
        async def handle_page(repos):
            for repo in repos:
                repo_id = repo.get("id")
                print(f"Processing repo: {repo.get('fullName')} (ID={repo_id})")
                payload = json.dumps({"repo_id": repo_id, "output_csv": output_csv})
                await Runner.run(feature_agent, payload)

        # Use process_all_repos to iterate through pages and invoke feature agent
        await process_all_repos(limit=num_repos, process_fn=handle_page)
        print(f"Processed and appended repositories to {output_csv}")


if __name__ == "__main__":
    asyncio.run(main(num_repos=144))
