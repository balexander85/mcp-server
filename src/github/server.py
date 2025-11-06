"""
First attempt at creating a MCP server

includes tools for managing github repositories

Model Context Protocol Python SDK Docs https://github.com/modelcontextprotocol/python-sdk
Github API Docs https://docs.github.com/en/rest/repos/repos
"""

from typing import List
import json

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from src.models.github import RepoData
from src.util import make_github_request


# Create MCP instance
mcp = FastMCP(name="GitHub Tools")


@mcp.tool(
    name="List Repositories",
    title="List GitHub Repositories",
    description="Fetches repositories from GitHub with optional filtering.",
)
async def get_repos(ctx: Context[ServerSession, None]) -> List[RepoData]:
    """Fetches an array of repositories from GitHub.

    This tool retrieves all repositories owned by the authenticated user.
    It uses the GitHub API token from environment variables for authentication.

    Args:
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        List[RepoData]: A list of RepoData objects representing forked repositories

    Example:
        repos = await get_forked_repos(ctx)
    """
    await ctx.info("Info: Starting processing")
    params = {
        "per_page": 100,
        "sort": "created",
        "direction": "asc",
    }
    url = "user/repos"  # Adjust per_page as needed
    repos: List[RepoData] = []
    while url:
        response = make_github_request(url, params=params)
        data = response.json()
        await ctx.info(f"response.request.url: {response.request.url}")
        for repo in data:
            repos.append(
                RepoData(
                    id=repo.get("id"),
                    owner=repo.get("owner", {}).get("login"),
                    name=repo.get("name"),
                    description=repo.get("description"),
                    url=repo.get("html_url"),
                    visibility=repo.get("visibility"),
                    fork=repo.get("fork"),
                    archived=repo.get("archived"),
                )
            )
        url = response.links.get("next", {}).get("url")  # Get the next page URL

    return repos


@mcp.tool(
    name="List Archived Repositories",
    title="List Archived GitHub Repositories",
    description="Fetches an array of archived repositories from GitHub.",
)
async def get_archived_repos(ctx: Context[ServerSession, None]) -> List[RepoData]:
    """Fetches an array of archived repositories from GitHub.

    This tool retrieves all archived repositories owned by the authenticated user.
    It uses the GitHub API token from environment variables for authentication.

    Args:
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        List[RepoData]: A list of RepoData objects representing archived repositories

    Example:
        repos = await get_archived_repos(ctx)
    """
    return [repo for repo in await get_repos(ctx) if repo.archived]


@mcp.tool(
    name="List Forked Repositories",
    title="List Forked GitHub Repositories",
    description="Fetches an array of forked repositories from GitHub.",
)
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
    return [repo for repo in await get_repos(ctx) if repo.fork]


@mcp.tool(
    name="Delete Repository",
    title="Delete GitHub Repository",
    description="Deletes a repository owned by a specific user.",
)
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
        delete_repo("johndoe", "my-project", ctx)
    """
    await ctx.info("Info: Starting deleting processing")
    response = make_github_request(url=f"repos/{owner}/{name}", method="DELETE")
    return response.status_code


@mcp.tool(
    name="Update Repository",
    title="Set Repository attribute",
    description="This tool updates a repository's attribute",
)
async def update_repo(
    owner: str, name: str, payload: dict, ctx: Context[ServerSession, None]
) -> int:
    """This tool updates a repository's attribute.

    Args:
        owner (str): The GitHub username or organization name that owns the repository
        name (str): The name of the repository to make private
        payload (dict): Object containing the attributes to be updated
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        int: The HTTP status code of the update request

    Example:
        status_code = await update_repo("johndoe", "my-project", {"visibility": "private"}, ctx)
    """
    await ctx.info(f"Info: Updating {owner}/{name} repo")
    response = make_github_request(
        url=f"repos/{owner}/{name}", method="PATCH", data=json.dumps(payload)
    )
    return response.status_code


@mcp.tool(
    name="Make Repository Private",
    title="Set Repository Privacy to Private",
    description="This tool updates a repository's visibility setting to private.",
)
async def make_repo_private(
    owner: str, name: str, ctx: Context[ServerSession, None]
) -> int:
    """This tool updates a repository's visibility setting to private.

    Args:
        owner (str): The GitHub username or organization name that owns the repository
        name (str): The name of the repository to make private
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        int: The HTTP status code of the update request

    Example:
        status_code = await make_repo_private("johndoe", "my-project", ctx)
    """
    await ctx.info(f"Info: Updating {name} to be private")
    data = {"visibility": "private"}
    return await update_repo(owner, name, data, ctx)


@mcp.tool(
    name="Unarchive Repository",
    title="Unarchive GitHub Repository",
    description="This tool unarchives a repository that was previously archived.",
)
async def unarchive_repo(
    owner: str, name: str, ctx: Context[ServerSession, None]
) -> int:
    """This tool unarchives a repository that was previously archived.

    Args:
        owner (str): The GitHub username or organization name that owns the repository
        name (str): The name of the repository to unarchive
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        int: The HTTP status code of the update request

    Example:
        status_code = await unarchive_repo("johndoe", "my-project", ctx)
    """
    await ctx.info(f"Info: Unarchiving {name}")
    data = {"archived": False}
    return await update_repo(owner, name, data, ctx)


@mcp.tool(
    name="Archive Repository",
    title="Archive GitHub Repository",
    description="This tool archives a repository, making it read-only.",
)
async def archive_repo(owner: str, name: str, ctx: Context[ServerSession, None]) -> int:
    """This tool archives a repository, making it read-only.

    Args:
        owner (str): The GitHub username or organization name that owns the repository
        name (str): The name of the repository to archive
        ctx (Context[ServerSession, None]): Context for the MCP server session

    Returns:
        int: The HTTP status code of the update request

    Example:
        status_code = await archive_repo("johndoe", "my-project", ctx)
    """
    await ctx.info(f"Info: Unarchiving {name}")
    data = {"archived": True}
    return await update_repo(owner, name, data, ctx)


if __name__ == "__main__":
    mcp.run()
