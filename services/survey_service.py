from utils.helper import generate_unique_id
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .upload_service import save_documents

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
    "documents_collected": DocumentsCollected,
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
            # property_id = survey["property_id"]
            property_id = survey.get("property_id", None)
            
            if not property_id:
                raise ValueError("property_id is required in survey_information")
            
            if not parcel_no:
                raise ValueError("parcel_no is required in survey_information")
            
            # create New SurveyId
            # survey.survey_id = generate_unique_id(self.db, SurveyInformation, "survey_id", 8, "SID")
            
            survey["survey_id"] = generate_unique_id(
            db= self.db,
            model=SurveyInformation,
            field_name="survey_id",
            size=8,
            prefix="SID"
        ),
            
            
        #       surveyor_id = generate_unique_id(
        #     db=self.db,
        #     model=SurveyInformation,
        #     field_name="survey_id",
        #     size=8,
        #     prefix="SUR"
        # ),
            
            payload["documents_collected"] = save_documents(
                property_id,
                payload.get("documents_collected", {})
            )
            
            
            # Check if the parcel already exists in the database
            parcel = (
            self.db.query(ParcelMaster)
            .filter(
                ParcelMaster.parcel_no == parcel_no,
                ParcelMaster.property_id == property_id
            )
            .first()
            )   
            
            # If the parcel does not exist, create a new ParcelMaster object
            if not parcel:
                parcel = ParcelMaster(
                    parcel_no=parcel_no,
                    property_id=property_id
                )
                self.db.add(parcel)
                self.db.flush()

            for section, model in MODEL_MAPPING.items():
                section_data = payload.get(section)
                if not section_data:
                    continue
                section_data["parcel_no"] = parcel.parcel_no
                section_data["property_id"] = parcel.property_id
                if not section_data:
                    continue

                obj = model(**section_data)
                self.db.add(obj)
                created_objects[section] = obj
                
            self.db.commit()

            return {
                "success": True,
                "message": "Survey saved successfully"
            }

        except SQLAlchemyError as e:

            self.db.rollback()

            raise e
        
    def save_bulk_surveys(self, surveys: list[dict]):
        results = []

        try:
            for survey in surveys:
                result = self.save_complete_survey(survey)
                results.append(result)

            self.db.commit()

            return {
                "message": "Bulk survey submitted successfully.",
                "total_records": len(results),
                "data": results
            }

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