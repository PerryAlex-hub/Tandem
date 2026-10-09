from app.crdt.board import Board


class BoardManager:
    def __init__(self) -> None:
        self.boards: dict[str, Board] = {}

    def get_or_create(self, room_code: str) -> Board:
        if room_code not in self.boards:
            self.boards[room_code] = Board()
        return self.boards[room_code]


board_manager = BoardManager()
