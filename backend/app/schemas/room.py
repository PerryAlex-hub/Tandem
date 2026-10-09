from datetime import datetime
from pydantic import BaseModel, ConfigDict
import uuid

class RoomOut(BaseModel):
    id: uuid.UUID
    code: str
    created_at: datetime
    current_problem_id: int | None

    model_config = ConfigDict(from_attributes=True)


class SetProblemRequest(BaseModel):
    frontend_id: int