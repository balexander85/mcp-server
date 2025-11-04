"""
First attempt at creating a MCP server

includes tools for managing github repositories
"""

from pydantic import BaseModel

from os import getenv
from typing import List, Literal
import json

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from dotenv import load_dotenv
import requests

# load environment variables
load_dotenv()
# Create MCP instance
mcp = FastMCP(name="Local MCP Server")

GITHUB_API_BASE_URL = "https://api.github.com/"


class RepoData(BaseModel):
    """
    Represents a repository from GitHub.

    Attributes:
        id: The repository ID.
        owner: The repository owner.
        name: The repository name.
        description: The repository description.
        url: The repository URL.
    """

    id: int
    owner: str
    name: str
    description: str | None
    url: str
    visibility: Literal["public"] | Literal["private"]
    fork: bool


## Github API Docs https://docs.github.com/en/rest/repos/repos


def get_github_token() -> str:
    token = getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")
    if not token.strip():
        raise ValueError("GITHUB_TOKEN environment variable is empty")
    return token


def make_github_request(url: str, method:  Literal["GET", "DELETE", "PATCH"] = "GET", **kwargs) -> requests.Response:
    """Make a GitHub API request with proper headers."""
    headers = {"Authorization": f"token {get_github_token()}"}
    if "headers" in kwargs:
        headers.update(kwargs["headers"])
    kwargs["headers"] = headers
    response = requests.request(method, GITHUB_API_BASE_URL + url, **kwargs)
    response.raise_for_status()
    return response


@mcp.tool()
async def get_forked_repos(ctx: Context[ServerSession, None]) -> List[RepoData]:
    """Fetches an array of forked repositories from GitHub.

    It uses token from environment variable to authenticate
    """
    await ctx.info("Info: Starting processing")
    params = {"per_page": 100, "sort": "created", "direction": "asc"}
    url = "user/repos"  # Adjust per_page as needed
    repos: List[RepoData] = []
    while url:
        response = make_github_request(url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        await ctx.info(f"response.request.url: {response.request.url}")
        for repo in data:
            if repo.get("fork"):
                repos.append(
                    RepoData(
                        id=repo.get("id"),
                        owner=repo.get("owner", {}).get("login"),
                        name=repo.get("name"),
                        description=repo.get("description"),
                        url=repo.get("html_url"),
                        visibility=repo.get("visibility"),
                        fork=repo.get("fork"),
                    )
                )
        url = response.links.get("next", {}).get("url")  # Get the next page URL

    return repos


@mcp.tool()
async def delete_repo(owner: str, name: str, ctx: Context[ServerSession, None]) -> int:
    """Deletes a select repo"""
    await ctx.info("Info: Starting deleting processing")
    response = make_github_request(url=f"repos/{owner}/{name}", method="DELETE")
    response.raise_for_status()
    return response.status_code


@mcp.tool()
async def make_repo_private(
    owner: str, name: str, ctx: Context[ServerSession, None]
) -> int:
    """Changes repo type to private"""
    await ctx.info(f"Info: Updating {name} to be private")
    data = {"visibility": "private"}
    response = make_github_request(
        url=f"repos/{owner}/{name}", method="PATCH", data=json.dumps(data)
    )
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    return response.status_code


@mcp.tool()
async def unarchive_repo(
    owner: str, name: str, ctx: Context[ServerSession, None]
) -> int:
    """Unarchive repo"""
    await ctx.info(f"Info: Unarchiving {name}")
    data = {"archived": False}
    response = make_github_request(
        f"repos/{owner}/{name}", method="PATCH", data=json.dumps(data)
    )
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    return response.status_code


@mcp.tool()
async def archive_repo(owner: str, name: str, ctx: Context[ServerSession, None]) -> int:
    """Archive repo"""
    await ctx.info(f"Info: Unarchiving {name}")
    data = {"archived": True}
    response = make_github_request(
        url=f"repos/{owner}/{name}", method="PATCH", data=json.dumps(data)
    )
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    return response.status_code


if __name__ == "__main__":
    # Run with SSE transport
    # Host and port are configured via environment variables
    mcp.run()

