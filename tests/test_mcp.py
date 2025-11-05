"""
Integration test for MCP server using requests
"""
import pytest
import requests


def test_mcp_server_running():
    """
    Test that the MCP server is running by making a GET request to the docs endpoint.
    """
    response = requests.get("http://localhost:8001/docs")
    # Assert that the response status code is 200 (OK)
    assert (
            response.status_code == 200
    ), f"Expected status code 200, but got {response.status_code}"


if __name__ == "__main__":
    pytest.main()
