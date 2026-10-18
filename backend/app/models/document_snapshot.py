from datetime import datetime

from sqlalchemy import String, LargeBinary, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DocumentSnapshot(Base):
    __tablename__ = "document_snapshots"

    room_code: Mapped[str] = mapped_column(String(8), primary_key=True)
    doc_type: Mapped[str] = mapped_column(String(20), primary_key=True)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
