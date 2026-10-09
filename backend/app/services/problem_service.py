import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.problem import Problem
from app.models.problem_catalog import ProblemCatalog


async def get_problem(db: AsyncSession, frontend_id: int) -> Problem | None:
    result = await db.execute(select(Problem).where(Problem.frontend_id == frontend_id))
    cached = result.scalar_one_or_none()
    if cached is not None:
        return cached

    result = await db.execute(select(ProblemCatalog).where(ProblemCatalog.frontend_id == frontend_id))
    catalog_entry = result.scalar_one_or_none()
    if catalog_entry is None:
        return None

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{settings.leetcode_api_base}/select/raw",
            params={"titleSlug": catalog_entry.title_slug},
        )
        response.raise_for_status()

    data = response.json()["question"]

    problem = Problem(
        frontend_id=frontend_id,
        title_slug=data["titleSlug"],
        title=data["title"],
        difficulty=data["difficulty"],
        description_html=data["content"],
        example_testcases=data["exampleTestcases"],
        topic_tags=data["topicTags"],
        code_snippets=data["codeSnippets"],
    )
    db.add(problem)
    await db.commit()
    await db.refresh(problem)
    return problem
