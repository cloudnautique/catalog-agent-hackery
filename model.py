# model.py - Contains CSV headers and Pydantic models for MCP repo feature extraction
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict

CSV_HEADERS = [
    "Repo Name",
    "Description",
    "Stars",
    "Forks",
    "Docker",
    "UVX",
    "NPX",
    "Filesystem Access",
    "Credentials",
    "License",
    "Example Activation Command(s)",
    "Readme",
    "Tools"
]

class RepoFeatureRow(BaseModel):
    repo_name: str
    description: str
    license: str
    stars: int
    forks: int
    docker: str
    uvx: str
    npx: str
    filesystem_access: str
    credentials: str
    example_activation_commands: str
    readme: str
    tools: str

class StrictMCPServerStdioParams(BaseModel):
    command: str
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    model_config = ConfigDict(extra="forbid")
