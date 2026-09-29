from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.problem import ProblemOut
from app.services.problem_service import get_problem

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("/{frontend_id}", response_model=ProblemOut)
async def get_problem_endpoint(frontend_id: int, db: AsyncSession = Depends(get_db)):
    problem = await get_problem(db, frontend_id)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return problem
