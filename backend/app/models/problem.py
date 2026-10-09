from sqlalchemy import String, Text, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Problem(Base):
    __tablename__ = "problems"

    frontend_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    title_slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    difficulty: Mapped[str] = mapped_column(String(10))
    description_html: Mapped[str] = mapped_column(Text)
    example_testcases: Mapped[str] = mapped_column(Text)
    topic_tags: Mapped[list] = mapped_column(JSON)
    code_snippets: Mapped[list] = mapped_column(JSON)
