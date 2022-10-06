from fastapi import FastAPI

from app.server.database import init_db
from app.server.routes.analysis_report import router as analysis_report_router

app = FastAPI()
app.include_router(analysis_report_router, tags=["Analysis Reports"], prefix="/analysis_report")


@app.on_event("startup")
async def start_db():
    await init_db()


@app.get("/", tags=["Root"])
async def read_root() -> dict:
    return {"message": "Welcome to your beanie powered app!"}
