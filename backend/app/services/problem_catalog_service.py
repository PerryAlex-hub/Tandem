from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problem_catalog import ProblemCatalog


async def search_problems(
    db: AsyncSession,
    query: str | None,
    difficulty: str | None,
    limit: int,
    offset: int,
) -> list[ProblemCatalog]:
    stmt = select(ProblemCatalog)

    if query:
        stmt = stmt.where(ProblemCatalog.title.ilike(f"%{query}%"))
    if difficulty:
        stmt = stmt.where(ProblemCatalog.difficulty == difficulty)

    stmt = stmt.order_by(ProblemCatalog.frontend_id).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return list(result.scalars().all())
