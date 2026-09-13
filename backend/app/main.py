from fastapi import FastAPI
from app.api.routes import rooms

app = FastAPI()
app.include_router(rooms.router)

@app.get("/")
def health():
    return {"message": "Backend is active!"}