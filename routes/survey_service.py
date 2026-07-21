from typing import Any, Dict, List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status,APIRouter
from sqlalchemy.orm import Session
from auth import verify_token
from core.database import get_db
from services.survey_service import SurveyService
from schema.survey_request import SurveyRequest
# from services.upload_service import save_document
from datetime import datetime



router = APIRouter()

# @router.post("/survey-form")
# def create_survey(
#     request: SurveyRequest,
#     db: Session = Depends(get_db)
# ):
#     return SurveyService(db).save_complete_survey(request)

@router.post("/survey-form")
def create_survey(
    request: SurveyRequest,
    db: Session = Depends(get_db)
):
    return SurveyService(db).save_complete_survey(
        request.model_dump(exclude_none=True)
    )
    
@router.post("/bulk-sync")
def create_bulk_surveys(
    requests: List[SurveyRequest],
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):

    return SurveyService(db).save_bulk_surveys(
        [request.model_dump(exclude_none=True) for request in requests]
    )
    
@router.post("/completed-survey-data")
def get_completed_survey_data(
    surveyor_id: str = Form(...),
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return SurveyService(db).get_completed_survey_data(surveyor_id)

@router.post("/upload-document")
async def upload_document(
    property_id: str = Form(...),
    files: List[UploadFile] = File(...),
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:

        uploaded_files = {}

        for file in files:

            document_name = file.filename.rsplit(".", 1)[0]

            file_path = save_document(
                property_id=property_id,
                document_name=document_name,
                file=file,
            )

            uploaded_files[document_name] = file_path

        return {
            "success": True,
            "property_id": property_id,
            "documents": uploaded_files,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.post("/all-survey-documents")
async def get_all_data(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        return SurveyService(db).get_all_survey_documents()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

# ):
#     payload = map_frontend_to_backend(request)

#     survey_request = SurveyRequest.model_validate(payload)

#     return SurveyService(db).save_complete_survey(
#         survey_request.model_dump(exclude_none=True)
#     )
    


def to_bool(value):
    """Convert Yes/No or boolean to bool."""
    if isinstance(value, bool):
        return value

    if value is None:
        return None

    return str(value).strip().lower() == "yes"


def to_float(value):
    if value in ("", None):
        return 0.0
    return float(value)


def to_int(value):
    if value in ("", None):
        return 0
    return int(float(value))


def to_datetime(value):
    if not value:
        return None

    return datetime.strptime(
        value,
        "%d/%m/%Y, %H:%M:%S"
    )


def to_date(value):
    if not value:
        return None

    return datetime.strptime(
        value,
        "%d/%m/%Y"
    ).date()

def map_document(value):
    return None if value is True else value

def map_frontend_to_backend(data: dict) -> dict:

    survey = data["surveys"]

    return {

        "survey_information": {

            "survey_id": survey["survey_id"],
            "parcel_no": survey["parcel_no"],
            "property_id": survey.get("property_id"),
            "survey_date": to_datetime(survey["survey_date"]),
            "surveyor_name": survey["surveyor_name"],
            "surveyor_id": survey["surveyor_id"],
            "ward_no": survey["ward_no"],
            "zone": survey["zone"],

            "colony_locality":
                survey["survey_info"]["colony"],

            "street_road_name":
                survey["survey_info"]["street_name"],

            "lane_no":
                survey["survey_info"]["lane_no"],

            "existing_property_id":
                survey["survey_info"]["existing_property_id"],

            "digital_door_number":
                survey["survey_info"]["ddn"],

            "gps_latitude":
                to_float(survey["survey_info"]["gps_latitude"]),

            "gps_longitude":
                to_float(survey["survey_info"]["gps_longitude"])
        },

        "owner_details": {

            "owner_name":
                survey["owner_details"]["owner_name"],

            "father_husband_name":
                survey["owner_details"]["father_husband_name"],

            "mobile_number":
                survey["owner_details"]["mobile_number"],

            "alternate_mobile":
                survey["owner_details"]["alternate_mobile"],

            "aadhaar_no":
                survey["owner_details"]["aadhaar_no"],

            "email":
                survey["owner_details"]["email_id"],

            "correspondence_address":
                survey["owner_details"]["correspondence_address"]
        },

        "occupier_details": {

            "occupier_name":
                survey["occupier_details"]["occupier_name"],

            "mobile_number":
                survey["occupier_details"]["occupier_mobile"],

            "occupancy_status":
                survey["occupier_details"]["occupancy_status"],

            "tenant_since":
                to_date(survey["occupier_details"]["tenant_since"])
        },

        "property_details": {

            "property_type":
                survey["property_details"]["property_type"],

            "property_status":
                survey["property_details"]["property_status"],

            "building_permission_available":
                to_bool(survey["property_details"]["building_permission"]),

            "property_ownership":
                survey["property_details"]["property_ownership"]
        },

        "land_building_information": {

            "plot_area":
                to_float(survey["land_building"]["plot_area"]),

            "ground_floor_area":
                to_float(survey["land_building"]["ground_floor"]),

            "first_floor_area":
                to_float(survey["land_building"]["first_floor"]),

            "second_floor_area":
                to_float(survey["land_building"]["second_floor"]),

            "third_floor_area":
                to_float(survey["land_building"]["third_floor"]),

            "number_of_floors":
                to_int(survey["land_building"]["number_of_floors"]),

            "year_of_construction":
                to_int(survey["land_building"]["year_construction"]),

            "total_builtup_area":
                to_float(survey["land_building"]["total_built_up"]),

            "building_age":
                to_int(survey["land_building"]["building_age"]),

            "construction_type":
                survey["land_building"]["construction_type"],

            "roof_type":
                survey["land_building"]["roof_type"]
        },

        "usage_details": {

            "primary_use":
                survey["usage_details"]["primary_use"],

            "mixed_use":
                to_bool(survey["usage_details"]["mixed_use"]),

            "commercial_activity":
                survey["usage_details"]["commercial_activity"],

            "occupancy":
                survey["usage_details"]["occupancy"],

            "number_of_families":
                to_int(survey["usage_details"]["number_of_families"]),

            "number_of_shops":
                to_int(survey["usage_details"]["number_of_shops"])
        },

        "tax_related_information": {

            "existing_property_tax_no":
                survey["tax_info"]["existing_tax_no"],

            "tax_paid_till":
                to_date(survey["tax_info"]["tax_paid_till"]),

            "outstanding_tax":
                to_float(survey["tax_info"]["outstanding_tax"]),

            "exempted_property":
                to_bool(survey["tax_info"]["exempted"]),

            "exemption_category":
                survey["tax_info"]["exemption_category"]
        },

        "utility_connections": {

            "water_connection_no":
                survey["utilities"]["water_connection"],

            "sewer_connection":
                to_bool(survey["utilities"]["sewer_connection"]),

            "electricity_consumer_no":
                survey["utilities"]["electricity_consumer"],

            "gas_connection":
                to_bool(survey["utilities"]["gas_connection"]),

            "trade_license_no":
                survey["utilities"]["trade_license"],

            "factory_license_no":
                survey["utilities"]["factory_license"]
        },

        "gis_information": {

            "gis_property_polygon_available":
                to_bool(survey["gis_info"]["polygon_available"]),

            "property_boundary_verified":
                to_bool(survey["gis_info"]["boundary_verified"]),

            "geo_tag_completed":
                to_bool(survey["gis_info"]["geo_tag_completed"]),

            "property_photo_captured":
                to_bool(survey["gis_info"]["property_photo"]),

            "front_elevation_photo":
                to_bool(survey["gis_info"]["front_elevation"]),

            "name_plate_photo":
                to_bool(survey["gis_info"]["name_plate"])
        },

        "smart_addressing": {

            "ddn_generated":
                to_bool(survey["smart_addressing"]["ddn_generated"]),

            "ddn_sticker_affixed":
                to_bool(survey["smart_addressing"]["ddn_sticker"]),

            "qr_code_affixed":
                to_bool(survey["smart_addressing"]["qr_code"]),

            "street_code":
                survey["smart_addressing"]["street_code"],

            "building_sequence_no":
                to_int(survey["smart_addressing"]["building_sequence"])
        },

        "verification": {

            "unassessed_property":
                survey["verification"]["unassessedProperty"],

            "under_assessed_property":
                survey["verification"]["underAssessedProperty"],

            "property_use_changed":
                survey["verification"]["propertyUseChanged"],

            "additional_floor_constructed":
                survey["verification"]["additionalFloorConstructed"],

            "boundary_changed":
                survey["verification"]["boundaryChanged"],

            "ownership_changed":
                survey["verification"]["ownershipChanged"],

            "demolished_property":
                survey["verification"]["demolishedProperty"],

            "new_property":
                survey["verification"]["newProperty"]
        },

        "documents_collected": {
                "aadhaar_copy": map_document(
                    survey["documents"]["aadhaarCopy"]
                ),
            "electricity_bill": map_document(
                survey["documents"]["electricityBill"]
            ),
            "water_bill": map_document(
                survey["documents"]["waterBill"]
            ),

            "sale_deed":map_document(
                survey["documents"]["saleDeed"]),

            "property_tax_receipt":map_document(
                survey["documents"]["propertyTaxReceipt"]),

            "building_permission":map_document(
                survey["documents"]["buildingPermissionDoc"]),

            "other_documents":map_document(
                survey["documents"].get("otherDocuments"))
        },

        "surveyor_remarks": {

            "surveyor_remarks":
                survey["surveyor_remarks"],

            "supervisor_remarks":
                survey["supervisor_remarks"]
        },

        "owner_declaration": {

            "owner_declaration_accepted":
                survey["owner_declaration"],

            "owner_signature":
                survey["owner_signature_path"],

            "owner_refusal_reason":
                None,

            "surveyor_signature":
                survey["surveyor_signature_path"],

            "declaration_date":
                to_datetime(survey["declaration_date"])
        }
    }
    
