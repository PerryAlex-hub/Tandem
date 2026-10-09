from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.problem import ProblemOut
from app.schemas.problem_catalog import ProblemCatalogOut
from app.services.problem_service import get_problem
from app.services.problem_catalog_service import search_problems

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("/search", response_model=list[ProblemCatalogOut])
async def search_problems_endpoint(
    q: str | None = None,
    difficulty: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await search_problems(db, q, difficulty, limit, offset)


@router.get("/{frontend_id}", response_model=ProblemOut)
async def get_problem_endpoint(frontend_id: int, db: AsyncSession = Depends(get_db)):
    problem = await get_problem(db, frontend_id)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return problem
