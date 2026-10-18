import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.routes import rooms, ws, problems
from app.core.snapshot_flush import flush_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    flush_task = asyncio.create_task(flush_loop())
    yield
    flush_task.cancel()


app = FastAPI(lifespan=lifespan)
app.include_router(rooms.router)
app.include_router(ws.router)
app.include_router(problems.router)

@app.get("/")
def health():
    return {"message": "Backend is active!"}