from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter


class InsertOp(BaseModel):
    type: Literal["insert"] = "insert"
    position: int
    text: str


class DeleteOp(BaseModel):
    type: Literal["delete"] = "delete"
    position: int
    count: int


Operation = Annotated[Union[InsertOp, DeleteOp], Field(discriminator="type")]
_operation_adapter = TypeAdapter(Operation)


def parse_operation(data: dict) -> InsertOp | DeleteOp:
    return _operation_adapter.validate_python(data)


def apply_op(content: str, op: InsertOp | DeleteOp) -> str:
    if isinstance(op, InsertOp):
        return content[:op.position] + op.text + content[op.position:]
    return content[:op.position] + content[op.position + op.count:]


def transform(op: InsertOp | DeleteOp, against: InsertOp | DeleteOp) -> InsertOp | DeleteOp:
    """Adjust `op` so it still applies correctly given that `against` has already been applied."""

    if isinstance(against, InsertOp) and isinstance(op, InsertOp):
        if op.position >= against.position:
            return InsertOp(position=op.position + len(against.text), text=op.text)
        return op

    if isinstance(against, InsertOp) and isinstance(op, DeleteOp):
        if against.position <= op.position:
            return DeleteOp(position=op.position + len(against.text), count=op.count)
        if against.position >= op.position + op.count:
            return op
        # the concurrent insert landed inside the range we meant to delete;
        # extend the delete so the new text gets removed too
        return DeleteOp(position=op.position, count=op.count + len(against.text))

    if isinstance(against, DeleteOp) and isinstance(op, InsertOp):
        if op.position <= against.position:
            return op
        if op.position >= against.position + against.count:
            return InsertOp(position=op.position - against.count, text=op.text)
        # the insertion point no longer exists; collapse to where the deleted range started
        return InsertOp(position=against.position, text=op.text)

    # delete vs delete
    op_start, op_end = op.position, op.position + op.count
    against_start, against_end = against.position, against.position + against.count

    overlap_start = max(op_start, against_start)
    overlap_end = min(op_end, against_end)
    overlap = max(0, overlap_end - overlap_start)
    new_count = op.count - overlap

    if op_start >= against_end:
        new_position = op_start - against.count
    elif op_start >= against_start:
        new_position = against_start
    else:
        new_position = op_start

    return DeleteOp(position=new_position, count=new_count)
