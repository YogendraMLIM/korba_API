from utils.helper import generate_unique_id
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .upload_service import save_base64_documents, save_single_base64_image
from sqlalchemy.inspection import inspect

from models import (
    ParcelMaster,
    SurveyInformation,
    OwnerDetails,
    OccupierDetails,
    PropertyDetails,
    LandBuildingInformation,
    UsageDetails,
    TaxRelatedInformation,
    UtilityConnections,
    GISInformation,
    SmartAddressing,
    Verification,
    DocumentsCollected,
    SurveyorRemarks,
    # OwnerDeclaration,
)

MODEL_MAPPING = {
    "survey_information": SurveyInformation,
    "owner_details": OwnerDetails,
    "occupier_details": OccupierDetails,
    "property_details": PropertyDetails,
    "land_building_information": LandBuildingInformation,
    "usage_details": UsageDetails,
    "tax_related_information": TaxRelatedInformation,
    "utility_connections": UtilityConnections,
    "gis_information": GISInformation,
    "smart_addressing": SmartAddressing,
    "verification": Verification,
    # "documents_collected": DocumentsCollected,
    "surveyor_remarks": SurveyorRemarks,
    # "owner_declaration": OwnerDeclaration,
}


class SurveyService:

    def __init__(self, db: Session):
        self.db = db
        
    def save_complete_survey(self, payload: dict):
        try:
            created_objects = {}

            survey = payload["survey_information"]

            parcel_no = survey.get("parcel_no")
            property_id = survey.get("property_id")

            if not parcel_no:
                raise ValueError("parcel_no is required in survey_information")

            if not property_id:
                raise ValueError("property_id is required in survey_information")

            # Generate Property UID
            property_uid = f"{parcel_no}{property_id}"

            # Generate Survey ID
            survey["survey_id"] = generate_unique_id(
                db=self.db,
                model=SurveyInformation,
                field_name="survey_id",
                size=8,
                prefix="SID"
            )

            survey["property_uid"] = property_uid

            # -----------------------------------
            # Save Documents
            # -----------------------------------
            saved_documents = save_base64_documents(
                parcel_no=parcel_no,
                property_id=property_id,
                documents=payload.get("documents_collected", {})
            )

            # -----------------------------------
            # Save GIS Images
            # -----------------------------------
            gis_info = payload.get("gis_information")

            if gis_info:

                gis_info["property_photo_path"] = save_single_base64_image(
                    parcel_no=parcel_no,
                    property_id=property_id,
                    category="gis",
                    file_name="property_photo",
                    file_data=(gis_info.get("property_photo_base64") or [None])[0]
                )

                gis_info["front_elevation_photo_path"] = save_single_base64_image(
                    parcel_no=parcel_no,
                    property_id=property_id,
                    category="gis",
                    file_name="front_elevation_photo",
                    file_data=(gis_info.get("front_elevation_photo_base64") or [None])[0]
                )

                gis_info["name_plate_photo_path"] = save_single_base64_image(
                    parcel_no=parcel_no,
                    property_id=property_id,
                    category="gis",
                    file_name="name_plate_photo",
                    file_data=(gis_info.get("name_plate_photo_base64") or [None])[0]
                )

                # Remove temporary frontend fields
                gis_info.pop("property_photo_base64", None)
                gis_info.pop("front_elevation_photo_base64", None)
                gis_info.pop("name_plate_photo_base64", None)

                # Remove old keys if present
                gis_info.pop("property_photo", None)

            # -----------------------------------
            # Create Parcel Master
            # -----------------------------------
            parcel = (
                self.db.query(ParcelMaster)
                .filter(ParcelMaster.property_uid == property_uid)
                .first()
            )

            if not parcel:
                parcel = ParcelMaster(
                    property_uid=property_uid,
                    parcel_no=parcel_no,
                    property_id=property_id
                )
                self.db.add(parcel)
                self.db.flush()

            # -----------------------------------
            # Save all sections
            # -----------------------------------
            for section, model in MODEL_MAPPING.items():

                if section == "documents_collected":
                    continue

                section_data = payload.get(section)

                if not section_data:
                    continue

                section_data["property_uid"] = property_uid

                if model is SurveyInformation:
                    section_data["parcel_no"] = parcel_no
                    section_data["property_id"] = property_id
                    section_data["property_location"] = (
                        section_data.get("property_location") or "Unknown"
                    )
                else:
                    section_data.pop("parcel_no", None)
                    section_data.pop("property_id", None)

                # Keep only columns defined in the SQLAlchemy model
                valid_columns = {
                    column.key
                    for column in inspect(model).mapper.column_attrs
                }

                section_data = {
                    key: value
                    for key, value in section_data.items()
                    if key in valid_columns
                }

                obj = model(**section_data)

                self.db.add(obj)
                created_objects[section] = obj

            # -----------------------------------
            # Save Document Records
            # -----------------------------------
            for doc in saved_documents:
                self.db.add(
                    DocumentsCollected(
                        property_uid=property_uid,
                        document_type=doc["document_type"],
                        file_path=doc["file_path"]
                    )
                )

            self.db.commit()

            return {
                "success": True,
                "message": "Survey submitted successfully.",
                "property_uid": property_uid,
                "survey_id": survey["survey_id"]
            }

        except SQLAlchemyError:
            self.db.rollback()
            raise

        except Exception:
            self.db.rollback()
            raise

    def get_completed_survey_data(self, surveyor_id: str):
        try:
            # Get all unique property IDs for the surveyor
            property_ids = (
                self.db.query(SurveyInformation.property_id)
                .filter(SurveyInformation.surveyor_id == surveyor_id)
                .distinct()
                .all()
            )

            property_ids = [row[0] for row in property_ids if row[0]]

            surveys = []

            for property_id in property_ids:
                survey_obj = {}

                for section, model in MODEL_MAPPING.items():
                    if hasattr(model, "property_id"):
                        data = (
                            self.db.query(model)
                            .filter(model.property_id == property_id)
                            .first()
                        )
                    else:
                        # SurveyInformation can also be queried by property_id
                        data = (
                            self.db.query(model)
                            .filter(model.property_id == property_id)
                            .first()
                        )

                    if data:
                        survey_obj[section] = {
                            column.name: getattr(data, column.name)
                            for column in data.__table__.columns
                        }

                surveys.append(survey_obj)

            return {
                "success": True,
                "count": len(surveys),
                "data": surveys
            }

        except Exception as e:
            self.db.rollback()
            raise e
        
    def get_all_survey_documents(self):
        try:
            documents = self.db.query(DocumentsCollected).all()
            return documents
        except Exception as e:
            self.db.rollback()
            raise e
