from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException

from app.server.models.analysis_report import AnalysisReport, CreateUpdateAnalysisReport
from app.server.services.analysis_report import TextAnalyzer


router = APIRouter()


@router.post("/", response_description="Analysis report added to the database.")
async def create_report(create_analysis_report: CreateUpdateAnalysisReport) -> dict:

    text_analyzer = TextAnalyzer(create_analysis_report)
    analysis_report = await text_analyzer.generate_analysis_report()
    await analysis_report.create()

    return {"message": f"Analysis report for text '{create_analysis_report.name}' added successfully."}


@router.get("/{name}", response_description="Analysis report loaded from database.")
async def get_analysis_report(name: str) -> AnalysisReport:
    review = await AnalysisReport.find_one(AnalysisReport.name == name)
    return review


@router.get("/", response_description="Analysis reports loaded from database.")
async def get_analysis_reports() -> list[AnalysisReport]:
    reviews = await AnalysisReport.find_all().to_list()
    return reviews


