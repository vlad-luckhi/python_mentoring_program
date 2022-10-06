from beanie import init_beanie
import motor.motor_asyncio

from app.server.models.analysis_report import AnalysisReport


async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://localhost:27017/analysis_reports"
    )

    await init_beanie(database=client.db_name, document_models=[AnalysisReport])
