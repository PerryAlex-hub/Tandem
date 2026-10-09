from pydantic import BaseModel


class ObjectOp(BaseModel):
    object_id: str
    object_type: str
    props: dict
    counter: int
    client_id: str
    deleted: bool = False
