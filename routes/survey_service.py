from typing import Any, Dict, List
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request, status
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from auth import verify_token
from core.database import get_db
from services.survey_service import SurveyService
from utils.helper import multipart_to_survey_payload



router = APIRouter()

# Save Survey Form Data into json (including GIS and other documents) to the database
@router.post("/survey-form")
def create_survey(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
):
    return SurveyService(db).save_complete_survey(request)

# Save Survey Form Data (including GIS and other documents) to the database
@router.post("/survey-form-submit")
async def submit_survey_form(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = await multipart_to_survey_payload(request)
    return SurveyService(db).submit_survey_form(payload)


# @router.post("/bulk-sync", dependencies=[Depends(verify_token)])
# def create_bulk_surveys(
#     requests: List[Dict[str, Any]],
#     db: Session = Depends(get_db),
# ):
#     return SurveyService(db).save_bulk_surveys(requests)


@router.post("/completed-survey-data-summary")
def get_completed_survey_data(
    request: dict = Body(...),
    db: Session = Depends(get_db),
):
    surveyor_id = request.get("surveyor_id")
    return SurveyService(db).get_completed_survey_data(surveyor_id)

@router.post("/survey-data-by-survey-id")
def get_survey_data_by_surveyor_id(
    request: dict = Body(...),
    db: Session = Depends(get_db),
):
    survey_id = request.get("survey_id")
    return SurveyService(db).get_survey_data_by_survey_id(survey_id)


# All survey documents (including GIS and other documents) for all surveys in the database
@router.post("/all-survey-documents")
async def get_all_data(
    db: Session = Depends(get_db),
):
    try:
        return SurveyService(db).get_all_survey_documents()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


# Retrun a list of existing property IDs from the survey data
@router.post("/existing-property-id-list")
def get_existing_property_ids(
    db: Session = Depends(get_db),
):
    return SurveyService(db).get_existing_property_ids()


# Get survey data by existing property ID
@router.post("/survey-data-by-existing-property-id")
def get_survey_data_by_existing_property_id(
    request: dict = Body(...),
    db: Session = Depends(get_db),
):
    existing_property_ids = request.get("existing_property_ids")

    if isinstance(existing_property_ids, str):
        existing_property_ids = [existing_property_ids]

    return SurveyService(db).get_survey_data_by_existing_property_id(
        existing_property_ids or []
    )
    
   
