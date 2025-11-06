"""
Integration test for MCP server using requests
"""

import pytest
import requests
from time import sleep


def test_mcp_server_running():
    """
    Test that the MCP server is running by making a GET request to the docs endpoint.
    """
    sleep(10)  # temp measure to give time for server to load
    response = requests.get("http://localhost:8001/docs")
    # Assert that the response status code is 200 (OK)
    assert (
        response.status_code == 200
    ), f"Expected status code 200, but got {response.status_code}"


def test_github_docs_available():
    """Checks that tool is available"""
    response = requests.get("http://localhost:8001/github/docs")
    assert (
        response.status_code == 200
    ), f"Expected status code 200, but got {response.status_code}"
    assert (
        len(response.json()) > 1
    ), f"Expected len of response.json() to be greater than 1, received: {len(response.json())}"


def test_get_time_method_available():
    """Checks that tool is available"""
    response = requests.post("http://localhost:8001/time/Get%20Time")
    assert (
            response.status_code == 200
    ), f"Expected status code 200, but got {response.status_code}"
    assert (
            len(response.json()) > 1
    ), f"Expected len of response.json() to be greater than 1, received: {len(response.json())}"


if __name__ == "__main__":
    pytest.main()
