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


if __name__ == "__main__":
    pytest.main()
