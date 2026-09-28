import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ParticipantJoin(BaseModel):
    display_name: str = Field(min_length=1, max_length=50)


class ParticipantOut(BaseModel):
    id: uuid.UUID
    display_name: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
