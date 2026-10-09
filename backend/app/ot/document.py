from app.ot.operations import DeleteOp, InsertOp, apply_op, transform


class OTDocument:
    def __init__(self) -> None:
        self.content: str = ""
        self.revision: int = 0
        self.history: list[InsertOp | DeleteOp] = []

    def receive_op(self, base_revision: int, op: InsertOp | DeleteOp) -> tuple[InsertOp | DeleteOp, int]:
        missed_ops = self.history[base_revision:]

        transformed = op
        for missed in missed_ops:
            transformed = transform(transformed, missed)

        self.content = apply_op(self.content, transformed)
        self.history.append(transformed)
        self.revision += 1

        return transformed, self.revision
