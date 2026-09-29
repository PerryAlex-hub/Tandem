from fastapi import FastAPI
from app.api.routes import rooms, ws, problems

app = FastAPI()
app.include_router(rooms.router)
app.include_router(ws.router)
app.include_router(problems.router)

@app.get("/")
def health():
    return {"message": "Backend is active!"}