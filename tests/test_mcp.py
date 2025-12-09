"""
Integration test for MCP server using requests
"""

from time import sleep
from datetime import datetime

import pytz
import pytest
import requests


BASE_URL = "http://localhost:8001"


@pytest.fixture(scope="class", autouse=True)
def wait_for_server(wait: int = 2):
    """Temporarily using sleep method until more advanced method is implemented"""
    sleep(wait)


class TestMCP:

    def test_mcp_server_running(self):
        """
        Test that the MCP server is running by making a GET request to the docs endpoint.
        """
        response = requests.get(f"{BASE_URL}/docs")
        # Assert that the response status code is 200 (OK)
        assert (
            response.status_code == 200
        ), f"Expected status code 200, but got {response.status_code}"


class TestGitHubMCP:

    def test_github_docs_available(self):
        """Checks that tool is available"""
        response = requests.get(f"{BASE_URL}/github/docs")
        assert (
            response.status_code == 200
        ), f"Expected status code 200, but got {response.status_code}"

    def test_get_repos_method(self):
        """Checks that tool is available"""
        response = requests.post(f"{BASE_URL}/github/get_repos")
        assert (
            response.status_code == 200
        ), f"Expected status code 200, but got {response.status_code}"
        assert (
            len(response.json()) > 1
        ), f"Expected len of response.json() to be greater than 1, received: {len(response.json())}"


class TestTimeMCP:

    @pytest.mark.parametrize(
        "payload",
        [{"time_zone": "America/Chicago"}, {}],
        ids=["timezone", "no timezone"],
    )
    def test_get_time_method(self, payload):
        """Checks that tool is available"""
        response = requests.post(f"{BASE_URL}/time/Get%20Time", json=payload)
        # Define the Central Time Zone
        central_timezone = pytz.timezone('America/Chicago')
        # Create date with Central Time Zone
        now_cdt = datetime.now(central_timezone)
        # Format the date
        today = now_cdt.strftime("%A, %B %d, %Y")
        assert (
            response.status_code == 200
        ), f"Expected status code 200, but got {response.status_code}"
        assert (
            type(response.content) == bytes
        ), f"Expected type of bytes, received: {type(response.content)}"
        assert today in str(
            response.content
        ), f"Expected today's date ({today}) in response.content ({response.content})"


if __name__ == "__main__":
    pytest.main()
