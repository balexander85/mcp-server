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
        visibility: Is repository public or private
        fork: Is repository forked?
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
    """Get GitHub token from environment variable.

    Returns:
        str: The GitHub API token

    Raises:
        ValueError: If GITHUB_TOKEN environment variable is not set or empty
    """
    token = getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")
    if not token.strip():
        raise ValueError("GITHUB_TOKEN environment variable is empty")
    return token


def make_github_request(
    url: str, method: Literal["GET", "DELETE", "PATCH"] = "GET", **kwargs
) -> requests.Response:
    """Make a GitHub API request with proper headers.

    Args:
        url (str): The GitHub API endpoint URL
        method (Literal["GET", "DELETE", "PATCH"]): HTTP method to use
        **kwargs: Additional arguments to pass to requests.request

    Returns:
        requests.Response: The HTTP response from GitHub API

    Raises:
        requests.RequestException: If the request fails
    """
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

    This tool retrieves all forked repositories owned by the authenticated user.
    It uses the GitHub API token from environment variables for authentication.

    Args:
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        List[RepoData]: A list of RepoData objects representing forked repositories

    Example:
        repos = await get_forked_repos(ctx)
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
    """Deletes a repository owned by a specific user.

    This tool permanently deletes a GitHub repository. The repository must be
    owned by the authenticated user.

    Args:
        owner (str): The GitHub username or organization name that owns the repository
        name (str): The name of the repository to delete
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        int: The HTTP status code of the deletion request (204 for success)

    Example:
        delete_repo("johnsmith", "my-project", ctx)
    """
    await ctx.info("Info: Starting deleting processing")
    response = make_github_request(url=f"repos/{owner}/{name}", method="DELETE")
    response.raise_for_status()
    return response.status_code


@mcp.tool()
async def make_repo_private(
    owner: str, name: str, ctx: Context[ServerSession, None]
) -> int:
    """Changes repository visibility to private.

    This tool updates a repository's visibility setting to private.

    Args:
        owner (str): The GitHub username or organization name that owns the repository
        name (str): The name of the repository to make private
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        int: The HTTP status code of the update request

    Example:
        status_code = await make_repo_private("johnsmith", "my-project", ctx)
    """
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
    """Unarchives a repository.

    This tool unarchives a repository that was previously archived.

    Args:
        owner (str): The GitHub username or organization name that owns the repository
        name (str): The name of the repository to unarchive
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        int: The HTTP status code of the update request

    Example:
        status_code = await unarchive_repo("johnsmith", "my-project", ctx)
    """
    await ctx.info(f"Info: Unarchiving {name}")
    data = {"archived": False}
    response = make_github_request(
        f"repos/{owner}/{name}", method="PATCH", data=json.dumps(data)
    )
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    return response.status_code


@mcp.tool()
async def archive_repo(owner: str, name: str, ctx: Context[ServerSession, None]) -> int:
    """Archives a repository.

    This tool archives a repository, making it read-only.

    Args:
        owner (str): The GitHub username or organization name that owns the repository
        name (str): The name of the repository to archive
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        int: The HTTP status code of the update request

    Example:
        status_code = await archive_repo("johnsmith", "my-project", ctx)
    """
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
