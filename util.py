from os import getenv
from typing import Literal

import requests
from dotenv import load_dotenv


# load environment variables
load_dotenv()

GITHUB_API_BASE_URL = "https://api.github.com/"


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
