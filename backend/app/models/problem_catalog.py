from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProblemCatalog(Base):
    __tablename__ = "problem_catalog"

    frontend_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    title_slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    difficulty: Mapped[str] = mapped_column(String(10))
