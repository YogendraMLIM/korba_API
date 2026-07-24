import json
import re
from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request, status
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from auth import verify_token
from core.database import get_db
from services.survey_service import MODEL_MAPPING, SurveyService
from services.upload_service import DOCUMENT_FIELDS


router = APIRouter()

SURVEY_SECTIONS = {
    "survey_information",
    "owner_details",
    "occupier_details",
    "property_details",
    "land_building_information",
    "usage_details",
    "tax_related_information",
    "utility_connections",
    "gis_information",
    "smart_addressing",
    "verification",
    "documents_collected",
    "surveyor_remarks",
}

GIS_FILE_FIELDS = {
    "property_photo": "property_photo_base64",
    "property_photo_base64": "property_photo_base64",
    "property_photo_path": "property_photo_base64",
    "front_elevation_photo": "front_elevation_photo_base64",
    "front_elevation_photo_base64": "front_elevation_photo_base64",
    "front_elevation_photo_path": "front_elevation_photo_base64",
    "name_plate_photo": "name_plate_photo_base64",
    "name_plate_photo_base64": "name_plate_photo_base64",
    "name_plate_photo_path": "name_plate_photo_base64",
}


def _build_flat_field_sections() -> dict[str, str]:
    field_sections: dict[str, str] = {}
    duplicate_fields = set()

    for section, model in MODEL_MAPPING.items():
        for attr in inspect(model).mapper.column_attrs:
            field_name = attr.key
            if field_name in {"id", "property_uid", "created_at", "updated_at"}:
                continue
            if field_name in field_sections:
                duplicate_fields.add(field_name)
                continue
            field_sections[field_name] = section

    for field_name in duplicate_fields:
        field_sections.pop(field_name, None)

    return field_sections


FLAT_FIELD_SECTIONS = _build_flat_field_sections()


def _parse_form_value(value: Any):
    if not isinstance(value, str):
        return value

    text = value.strip()
    if text == "":
        return ""

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return value


def _field_parts(field_name: str) -> list[str]:
    normalized = re.sub(r"\[([^\]]+)\]", r".\1", field_name)
    parts = [part for part in normalized.split(".") if part]

    if parts and parts[0] in {"payload", "data", "survey_data"}:
        parts = parts[1:]
    if parts and parts[0] == "gis_info":
        parts[0] = "gis_information"

    return parts


def _set_nested_value(payload: dict, field_name: str, value: Any):
    parts = _field_parts(field_name)
    if not parts:
        return

    if len(parts) == 1 and parts[0] in FLAT_FIELD_SECTIONS:
        payload.setdefault(FLAT_FIELD_SECTIONS[parts[0]], {})[parts[0]] = value
        return

    current = payload
    for part in parts[:-1]:
        current = current.setdefault(part, {})

    leaf = parts[-1]
    if leaf in current:
        if not isinstance(current[leaf], list):
            current[leaf] = [current[leaf]]
        current[leaf].append(value)
    else:
        current[leaf] = value


#   Append file data to the appropriate section in the survey payload based on field name and hints
def _append_file(
    payload: dict,
    field_name: str,
    file_data: dict,
    filename: str | None = None,
):
    parts = _field_parts(field_name)
    leaf = parts[-1] if parts else field_name
    parent = parts[-2] if len(parts) > 1 else None
    file_hint = f"{field_name} {filename or ''}".lower()

    if leaf in GIS_FILE_FIELDS or parent == "gis_information":
        gis_field = GIS_FILE_FIELDS.get(leaf, leaf)
        payload.setdefault("gis_information", {}).setdefault(gis_field, []).append(file_data)
        return

    for gis_name, gis_field in GIS_FILE_FIELDS.items():
        if gis_name in file_hint:
            payload.setdefault("gis_information", {}).setdefault(gis_field, []).append(file_data)
            return

    document_field = leaf
    if document_field in DOCUMENT_FIELDS:
        document_field = f"{document_field}_files"

    if document_field.endswith("_files"):
        payload.setdefault("documents_collected", {}).setdefault(document_field, []).append(file_data)
        return

    for field in DOCUMENT_FIELDS:
        if field in file_hint:
            payload.setdefault("documents_collected", {}).setdefault(f"{field}_files", []).append(file_data)
            return

    payload.setdefault("documents_collected", {}).setdefault("other_documents_files", []).append(file_data)


# Convert multipart/form-data request to a structured survey payload
async def _multipart_to_survey_payload(request: Request) -> dict:
    payload: dict[str, Any] = {}
    form = await request.form()

    for key, value in form.multi_items():
        if hasattr(value, "filename") and hasattr(value, "read"):
            content = await value.read()
            if not content:
                continue

            file_data = {
                "filename": value.filename,
                "content_type": value.content_type or "application/octet-stream",
                "content": content,
            }
            _append_file(payload, key, file_data, value.filename)
            continue

        parsed_value = _parse_form_value(value)

        if key in {"payload", "data", "survey_data"}:
            if isinstance(parsed_value, dict):
                payload.update(parsed_value)
            continue

        if key == "gis_info":
            payload.setdefault("gis_information", {})
            if isinstance(parsed_value, dict):
                payload["gis_information"].update(parsed_value)
            continue

        if isinstance(parsed_value, dict) and key in SURVEY_SECTIONS:
            payload.setdefault(key, {})
            payload[key].update(parsed_value)
            continue

        _set_nested_value(payload, key, parsed_value)

    return payload


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
    payload = await _multipart_to_survey_payload(request)
    return SurveyService(db).submit_survey_form(payload)


@router.post("/bulk-sync", dependencies=[Depends(verify_token)])
def create_bulk_surveys(
    requests: List[Dict[str, Any]],
    db: Session = Depends(get_db),
):
    return SurveyService(db).save_bulk_surveys(requests)


@router.post("/completed-survey-data", dependencies=[Depends(verify_token)])
def get_completed_survey_data(
    surveyor_id: str = Form(...),
    db: Session = Depends(get_db),
):
    return SurveyService(db).get_completed_survey_data(surveyor_id)


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
    
   
