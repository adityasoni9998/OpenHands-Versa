from pydantic import BaseModel, Field

__all__ = ['ObservationType']


class ObservationTypeSchema(BaseModel):
    READ: str = Field(default='read')
    """The content of a file
    """

    WRITE: str = Field(default='write')

    EDIT: str = Field(default='edit')

    BROWSE: str = Field(default='browse')
    """The HTML content of a URL
    """

    RUN: str = Field(default='run')
    """The output of a command
    """

    RUN_IPYTHON: str = Field(default='run_ipython')
    """Runs a IPython cell.
    """

    CHAT: str = Field(default='chat')
    """A message from the user
    """

    DELEGATE: str = Field(default='delegate')
    """The result of a task delegated to another agent
    """

    MESSAGE: str = Field(default='message')

    ERROR: str = Field(default='error')

    SUCCESS: str = Field(default='success')

    NULL: str = Field(default='null')

    THINK: str = Field(default='think')

    AGENT_STATE_CHANGED: str = Field(default='agent_state_changed')

    USER_REJECTED: str = Field(default='user_rejected')

    CONDENSE: str = Field(default='condense')
    """Result of a condensation operation."""

    SEARCH: str = Field(default='search')
    """Result of querying a search engine."""

    DOWNLOAD: str = Field(default='download')
    """Result of downloading/opening a file via the browser"""


ObservationType = ObservationTypeSchema()
