"""
Integration test for MCP server using requests
"""

import pytest
import requests
from time import sleep

BASE_URL = "http://localhost:8001"


def wait_for_server(wait: int = 3):
    """Temporarily using sleep method until more advanced method is implemented"""
    sleep(wait)


class TestMCP:

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        wait_for_server()

    def test_mcp_server_running(self):
        """
        Test that the MCP server is running by making a GET request to the docs endpoint.
        """
        response = requests.get(f"{BASE_URL}/docs")
        # Assert that the response status code is 200 (OK)
        assert (
            response.status_code == 200
        ), f"Expected status code 200, but got {response.status_code}"


    def test_github_docs_available(self):
        """Checks that tool is available"""
        response = requests.get(f"{BASE_URL}/github/docs")
        assert (
            response.status_code == 200
        ), f"Expected status code 200, but got {response.status_code}"


    def test_get_time_method_available(self):
        """Checks that tool is available"""
        timezone = {"time_zone": "America/Chicago"}
        response = requests.post(f"{BASE_URL}/time/Get%20Time", json=timezone)
        assert (
            response.status_code == 200
        ), f"Expected status code 200, but got {response.status_code}"
        assert (
            len(response.json()) > 1
        ), f"Expected len of response.json() to be greater than 1, received: {len(response.json())}"


    def test_get_time_method_available_no_timezone(self):
        """Checks that tool is available"""
        response = requests.post(f"{BASE_URL}/time/Get%20Time", json={})
        assert (
                response.status_code == 200
        ), f"Expected status code 200, but got {response.status_code}"
        assert (
                len(response.json()) > 1
        ), f"Expected len of response.json() to be greater than 1, received: {len(response.json())}"


if __name__ == "__main__":
    pytest.main()
