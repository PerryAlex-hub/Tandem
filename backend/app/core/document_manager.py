from app.ot.document import OTDocument


class DocumentManager:
    def __init__(self) -> None:
        self.documents: dict[str, OTDocument] = {}

    def get_or_create(self, room_code: str) -> OTDocument:
        if room_code not in self.documents:
            self.documents[room_code] = OTDocument()
        return self.documents[room_code]


document_manager = DocumentManager()
