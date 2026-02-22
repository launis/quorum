from pydantic import BaseModel


class UserDeleteResponse(BaseModel):
    """Response after deleting a user."""

    status: str
    uid: str
