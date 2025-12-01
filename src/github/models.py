from typing import Literal

from pydantic import BaseModel


class RepoData(BaseModel):
    """
    Represents a repository from GitHub.

    Attributes:
        name: The repository name.
        description: The repository description.
        url: The repository URL.
        visibility: Is repository public or private
        fork: Is repository forked
        archived: Is the repository archived
    """

    name: str
    description: str | None
    url: str
    visibility: Literal["public"] | Literal["private"]
    fork: bool
    archived: bool
