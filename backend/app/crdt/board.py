from app.crdt.objects import ObjectOp


class Board:
    def __init__(self) -> None:
        self.objects: dict[str, ObjectOp] = {}

    def apply_op(self, op: ObjectOp) -> ObjectOp:
        existing = self.objects.get(op.object_id)
        incoming_clock = (op.counter, op.client_id)

        if existing is None or incoming_clock > (existing.counter, existing.client_id):
            self.objects[op.object_id] = op

        return self.objects[op.object_id]

    def get_all(self) -> list[dict]:
        return [obj.model_dump() for obj in self.objects.values()]
