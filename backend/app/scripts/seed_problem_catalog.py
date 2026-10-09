import asyncio

import httpx
from sqlalchemy.dialects.postgresql import insert

from app.db.session import AsyncSessionLocal
from app.models.problem_catalog import ProblemCatalog

LEETCODE_API_BASE = "http://127.0.0.1:3001"
PAGE_SIZE = 100


async def fetch_page(client: httpx.AsyncClient, skip: int) -> list[dict]:
    response = await client.get(
        f"{LEETCODE_API_BASE}/problems",
        params={"limit": PAGE_SIZE, "skip": skip},
    )
    response.raise_for_status()
    data = response.json()
    return data["problemsetQuestionList"]


async def upsert_page(db, problems: list[dict]) -> None:
    values = [
        {
            "frontend_id": int(p["questionFrontendId"]),
            "title_slug": p["titleSlug"],
            "title": p["title"],
            "difficulty": p["difficulty"],
        }
        for p in problems
    ]

    stmt = insert(ProblemCatalog).values(values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["frontend_id"],
        set_={
            "title_slug": stmt.excluded.title_slug,
            "title": stmt.excluded.title,
            "difficulty": stmt.excluded.difficulty,
        },
    )
    await db.execute(stmt)
    await db.commit()


async def main() -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with AsyncSessionLocal() as db:
            skip = 0
            while True:
                problems = await fetch_page(client, skip)
                if not problems:
                    break

                await upsert_page(db, problems)
                skip += PAGE_SIZE
                print(f"Seeded {skip} problems...")


if __name__ == "__main__":
    asyncio.run(main())
