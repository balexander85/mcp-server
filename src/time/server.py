import datetime

from mcp.server.fastmcp import FastMCP
import pytz

mcp = FastMCP(name="Time Tools")


@mcp.tool(
    name="Get Time",
    title="List Current Time",
    description="This tool returns current time for America/Chicago timezone.",
)
async def get_time(time_zone: str = "America/Chicago") -> str:
    """Fetches the current date and time in CDT (Central Daylight Time).

    Args:
        time_zone: string time zone defaults to America/Chicago

    Returns:
      A string representing the date and time in the format:
      "Weekday, Month Day, Year, at Hour:Minute AM/PM CDT"
    """
    cdt_timezone = pytz.timezone(time_zone)
    now_cdt = datetime.datetime.now(cdt_timezone)

    # Format the output string
    formatted_datetime = now_cdt.strftime("%A, %B %d, %Y, at %I:%M %p %Z")

    return formatted_datetime


if __name__ == "__main__":
    mcp.run()
