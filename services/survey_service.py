import re
from datetime import date, datetime
from utils.helper import multipart_to_survey_payload, repoint_property_uid, to_dict, to_str_or_none, first_item,  sanitize_for_model, apply_model_defaults, upsert_by_property_uid, upsert_land_building_area, upsert_document_record, extract_land_building_areas, find_existing_parcel_for_survey
from utils.generate_id import generate_unique_id
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from .upload_service import (
    save_base64_documents,
    save_single_base64_image,
    save_single_upload_image,
    save_upload_documents,
)
from sqlalchemy.inspection import inspect
from utils.survey_constants import (
    MODEL_MAPPING,
    MODEL_DEFAULTS,
)
from models import (
    ParcelMaster,
    SurveyInformation,
    OwnerDetails,
    OccupierDetails,
    PropertyDetails,
    LandBuildingInformation,
    LandBuildingArea,
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

class SurveyService:

    def __init__(self, db: Session):
        self.db = db

 
    # Save Complete Survey In json Format  
    # def save_complete_survey(self, payload: dict, files_are_uploads: bool = False):
    #     try:
    #         payload = to_dict(payload)
    #         survey = to_dict(payload.get("survey_information"))
    #         payload["survey_information"] = survey

    #         parcel_no = to_str_or_none(survey.get("parcel_no"))
    #         property_id = to_str_or_none(survey.get("property_id"))
    #         existing_parcel = find_existing_parcel_for_survey(self, survey)

    #         if existing_parcel:
    #             property_uid = existing_parcel.property_uid
    #             parcel_no = parcel_no or existing_parcel.parcel_no
    #             property_id = property_id or existing_parcel.property_id
    #         elif parcel_no and property_id:
    #             property_uid = f"{parcel_no}{property_id}"
    #         else:
    #             property_uid = to_str_or_none(survey.get("property_uid"))
    #             if not property_uid:
    #                 property_uid = generate_unique_id(
    #                     db=self.db,
    #                     model=ParcelMaster,
    #                     field_name="property_uid",
    #                     size=10,
    #                     prefix="PUID"
    #                 )

    #             if not parcel_no:
    #                 parcel_no = f"AUTO-{property_uid[-6:]}"
    #             if not property_id:
    #                 property_id = f"AUTO-{property_uid[:6]}"

    #         survey["parcel_no"] = parcel_no
    #         survey["property_id"] = property_id
    #         survey["property_uid"] = property_uid

    #         # Generate Survey ID
    #         existing_survey = (
    #             self.db.query(SurveyInformation)
    #             .filter(SurveyInformation.property_uid == property_uid)
    #             .first()
    #         )
    #         if existing_survey and not to_str_or_none(survey.get("survey_id")):
    #             survey["survey_id"] = existing_survey.survey_id
    #         elif not to_str_or_none(survey.get("survey_id")):
    #             survey["survey_id"] = generate_unique_id(
    #                 db=self.db,
    #                 model=SurveyInformation,
    #                 field_name="survey_id",
    #                 size=8,
    #                 prefix="SID"
    #             )

    #         survey["property_uid"] = property_uid

    #         # -----------------------------------
    #         # Save Documents
    #         # -----------------------------------
    #         documents_collected = to_dict(payload.get("documents_collected"))
    #         if files_are_uploads:
    #             saved_documents = save_upload_documents(
    #                 parcel_no=parcel_no,
    #                 property_id=property_id,
    #                 documents=documents_collected
    #             )
    #         else:
    #             saved_documents = save_base64_documents(
    #                 parcel_no=parcel_no,
    #                 property_id=property_id,
    #                 documents=documents_collected
    #             )

    #         # -----------------------------------
    #         # Save GIS Images
    #         # -----------------------------------
    #         gis_info = to_dict(payload.get("gis_information"))

    #         if gis_info:
    #             if files_are_uploads:
    #                 property_photo_path = save_single_upload_image(
    #                     parcel_no=parcel_no,
    #                     property_id=property_id,
    #                     category="gis",
    #                     file_name="property_photo",
    #                     upload=first_item(gis_info.get("property_photo_base64"))
    #                 )
    #             else:
    #                 property_photo_path = save_single_base64_image(
    #                     parcel_no=parcel_no,
    #                     property_id=property_id,
    #                     category="gis",
    #                     file_name="property_photo",
    #                     file_data=first_item(gis_info.get("property_photo_base64"))
    #                 )
    #             if property_photo_path:
    #                 gis_info["property_photo_path"] = property_photo_path

    #             if files_are_uploads:
    #                 front_elevation_photo_path = save_single_upload_image(
    #                     parcel_no=parcel_no,
    #                     property_id=property_id,
    #                     category="gis",
    #                     file_name="front_elevation_photo",
    #                     upload=first_item(gis_info.get("front_elevation_photo_base64"))
    #                 )
    #             else:
    #                 front_elevation_photo_path = save_single_base64_image(
    #                     parcel_no=parcel_no,
    #                     property_id=property_id,
    #                     category="gis",
    #                     file_name="front_elevation_photo",
    #                     file_data=first_item(gis_info.get("front_elevation_photo_base64"))
    #                 )
    #             if front_elevation_photo_path:
    #                 gis_info["front_elevation_photo_path"] = front_elevation_photo_path

    #             if files_are_uploads:
    #                 name_plate_photo_path = save_single_upload_image(
    #                     parcel_no=parcel_no,
    #                     property_id=property_id,
    #                     category="gis",
    #                     file_name="name_plate_photo",
    #                     upload=first_item(gis_info.get("name_plate_photo_base64"))
    #                 )
    #             else:
    #                 name_plate_photo_path = save_single_base64_image(
    #                     parcel_no=parcel_no,
    #                     property_id=property_id,
    #                     category="gis",
    #                     file_name="name_plate_photo",
    #                     file_data=first_item(gis_info.get("name_plate_photo_base64"))
    #                 )
    #             if name_plate_photo_path:
    #                 gis_info["name_plate_photo_path"] = name_plate_photo_path

    #             # Remove temporary frontend fields
    #             gis_info.pop("property_photo_base64", None)
    #             gis_info.pop("front_elevation_photo_base64", None)
    #             gis_info.pop("name_plate_photo_base64", None)

    #             # Remove old keys if present
    #             gis_info.pop("property_photo", None)

    #         # -----------------------------------
    #         # Create Parcel Master
    #         # -----------------------------------
    #         parcel = (
    #             self.db.query(ParcelMaster)
    #             .filter(ParcelMaster.property_uid == property_uid)
    #             .first()
    #         )

    #         if not parcel:
    #             parcel = ParcelMaster(
    #                 property_uid=property_uid,
    #                 parcel_no=parcel_no,
    #                 property_id=property_id,
    #                 existing_property_id=survey.get("existing_property_id")
    #             )
    #             self.db.add(parcel)
    #             self.db.flush()
    #         else:
    #             parcel.parcel_no = parcel_no or parcel.parcel_no
    #             parcel.property_id = property_id or parcel.property_id
    #             parcel.existing_property_id = (
    #                 survey.get("existing_property_id")
    #                 or parcel.existing_property_id
    #             )

    #         # -----------------------------------
    #         # Save all sections
    #         # -----------------------------------
    #         land_building_area_rows = []

    #         for section, model in MODEL_MAPPING.items():

    #             if section == "documents_collected":
    #                 continue

    #             section_data = to_dict(payload.get(section))

    #             if not section_data:
    #                 continue

    #             section_data = dict(section_data)
    #             section_data["property_uid"] = property_uid

    #             if model is SurveyInformation:
    #                 section_data["parcel_no"] = parcel_no
    #                 section_data["property_id"] = property_id
    #                 if str(section_data.get("property_location", "")).strip().lower() == "other":
    #                     section_data["property_location"] = section_data.get("property_location_other") or "Unknown"
    #                 else:
    #                     section_data["property_location"] = section_data.get("property_location") or "Unknown"

    #             else:
    #                 section_data.pop("parcel_no", None)
    #                 section_data.pop("property_id", None)

    #             if model is LandBuildingInformation:
    #                 land_building_area_rows = extract_land_building_areas(
    #                     self,
    #                     section_data=section_data,
    #                     property_uid=property_uid,
    #                     surveyor_id=survey.get("surveyor_id")
    #                 )

    #             section_data = sanitize_for_model(model, section_data)
    #             section_data = apply_model_defaults(model, section_data)

    #             upsert_by_property_uid(self, model, section_data)

    #         for area_row in land_building_area_rows:
    #             upsert_land_building_area(self, area_row)

    #         # -----------------------------------
    #         # Save Document Records
    #         # -----------------------------------
    #         for doc in saved_documents:
    #             upsert_document_record(self, doc, property_uid)

    #         self.db.commit()

    #         return {
    #             "success": True,
    #             "message": "Survey submitted successfully.",
    #             "property_uid": property_uid,
    #             "survey_id": survey["survey_id"]
    #         }

    #     except SQLAlchemyError:
    #         self.db.rollback()
    #         raise

    #     except Exception:
    #         self.db.rollback()
    #         raise
    
    def save_complete_survey(self, payload: dict, files_are_uploads: bool = False):
        try:
            payload = to_dict(payload)
            survey = to_dict(payload.get("survey_information"))
            payload["survey_information"] = survey
    
            parcel_no = to_str_or_none(survey.get("parcel_no"))
            property_id = to_str_or_none(survey.get("property_id"))
            existing_property_id = to_str_or_none(survey.get("existing_property_id"))
            
    
            existing_parcel = find_existing_parcel_for_survey(self, survey)
    
            is_resurvey = bool(existing_parcel)
            old_property_uid = existing_parcel.property_uid if existing_parcel else None
    
            if is_resurvey:
                # existing_property_id is frozen -- never overwritten once set.
                existing_property_id = existing_property_id or existing_parcel.existing_property_id
    
                # property_uid is refreshed on every re-survey.
                property_uid = generate_unique_id(
                    db=self.db,
                    model=ParcelMaster,
                    field_name="property_uid",
                    size=10,
                    prefix="PUID"
                )
                # parcel_no / property_id: honor whatever the caller sent for
                # this re-survey; only fall back to auto-generated values if
                if not parcel_no:
                    parcel_no = f"AUTO-{property_uid[-6:]}"
                if not property_id:
                    property_id = f"AUTO-{property_uid[:6]}"
    
            elif parcel_no and property_id:
                property_uid = f"{parcel_no}{property_id}"
    
            else:
                property_uid = to_str_or_none(survey.get("property_uid"))
                if not property_uid:
                    property_uid = generate_unique_id(
                        db=self.db,
                        model=ParcelMaster,
                        field_name="property_uid",
                        size=10,
                        prefix="PUID"
                    )
                if not parcel_no:
                    parcel_no = f"AUTO-{property_uid[-6:]}"
                if not property_id:
                    property_id = f"AUTO-{property_uid[:6]}"
    
            survey["parcel_no"] = parcel_no
            survey["property_id"] = property_id
            survey["property_uid"] = property_uid
            survey["existing_property_id"] = existing_property_id
    
            # -----------------------------------
            # survey_id is ALWAYS regenerated -- no reuse branch anymore.
            # -----------------------------------
            survey["survey_id"] = generate_unique_id(
                db=self.db,
                model=SurveyInformation,
                field_name="survey_id",
                size=8,
                prefix="SID"
            )
    
            # -----------------------------------
            # Re-point every existing row from the OLD property_uid to the
            # NEW one BEFORE the section upsert loop runs, so those upserts
            # (which match on property_uid) update the same rows instead of
            # inserting duplicates.
            # -----------------------------------
            if is_resurvey and old_property_uid and old_property_uid != property_uid:
                repoint_property_uid(self, old_property_uid, property_uid)
    
            # -----------------------------------
            # Save Documents
            # -----------------------------------
            documents_collected = to_dict(payload.get("documents_collected"))
            if files_are_uploads:
                saved_documents = save_upload_documents(
                    parcel_no=parcel_no,
                    property_id=property_id,
                    documents=documents_collected
                )
            else:
                saved_documents = save_base64_documents(
                    parcel_no=parcel_no,
                    property_id=property_id,
                    documents=documents_collected
                )
    
            # -----------------------------------
            # Save GIS Images
            # -----------------------------------
            gis_info = to_dict(payload.get("gis_information"))
    
            if gis_info:
                if files_are_uploads:
                    property_photo_path = save_single_upload_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="property_photo",
                        upload=first_item(gis_info.get("property_photo_base64"))
                    )
                else:
                    property_photo_path = save_single_base64_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="property_photo",
                        file_data=first_item(gis_info.get("property_photo_base64"))
                    )
                if property_photo_path:
                    gis_info["property_photo_path"] = property_photo_path
    
                if files_are_uploads:
                    front_elevation_photo_path = save_single_upload_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="front_elevation_photo",
                        upload=first_item(gis_info.get("front_elevation_photo_base64"))
                    )
                else:
                    front_elevation_photo_path = save_single_base64_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="front_elevation_photo",
                        file_data=first_item(gis_info.get("front_elevation_photo_base64"))
                    )
                if front_elevation_photo_path:
                    gis_info["front_elevation_photo_path"] = front_elevation_photo_path
    
                if files_are_uploads:
                    name_plate_photo_path = save_single_upload_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="name_plate_photo",
                        upload=first_item(gis_info.get("name_plate_photo_base64"))
                    )
                else:
                    name_plate_photo_path = save_single_base64_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="name_plate_photo",
                        file_data=first_item(gis_info.get("name_plate_photo_base64"))
                    )
                if name_plate_photo_path:
                    gis_info["name_plate_photo_path"] = name_plate_photo_path
    
                gis_info.pop("property_photo_base64", None)
                gis_info.pop("front_elevation_photo_base64", None)
                gis_info.pop("name_plate_photo_base64", None)
                gis_info.pop("property_photo", None)
    
            # -----------------------------------
            # Create / Update Parcel Master
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
                    property_id=property_id,
                    existing_property_id=existing_property_id
                )
                self.db.add(parcel)
                self.db.flush()
            else:
                # All other values refresh on re-survey ...
                parcel.parcel_no = parcel_no
                parcel.property_id = property_id
                # ... except existing_property_id, which is frozen.
                parcel.existing_property_id = (
                    parcel.existing_property_id or existing_property_id
                )
    
            # -----------------------------------
            # Save all sections
            # -----------------------------------
            land_building_area_rows = []
    
            for section, model in MODEL_MAPPING.items():
    
                if section == "documents_collected":
                    continue
    
                section_data = to_dict(payload.get(section))
    
                if not section_data:
                    continue
    
                section_data = dict(section_data)
                section_data["property_uid"] = property_uid
    
                if model is SurveyInformation:
                    section_data["parcel_no"] = parcel_no
                    section_data["property_id"] = property_id
                    if str(section_data.get("property_location", "")).strip().lower() == "other":
                        section_data["property_location"] = section_data.get("property_location_other") or "Unknown"
                    else:
                        section_data["property_location"] = section_data.get("property_location") or "Unknown"
    
                else:
                    section_data.pop("parcel_no", None)
                    section_data.pop("property_id", None)
    
                if model is LandBuildingInformation:
                    land_building_area_rows = extract_land_building_areas(
                        self,
                        section_data=section_data,
                        property_uid=property_uid,
                        surveyor_id=survey.get("surveyor_id")
                    )
    
                section_data = sanitize_for_model(model, section_data)
                section_data = apply_model_defaults(model, section_data)
    
                # This now UPDATEs the re-pointed row (matched on the fresh
                # property_uid) if it exists, or INSERTs fresh if it doesn't --
                # i.e. every incoming field replaces the stored value.
                upsert_by_property_uid(self, model, section_data)
    
            for area_row in land_building_area_rows:
                upsert_land_building_area(self, area_row)
    
            # -----------------------------------
            # Save Document Records
            # -----------------------------------
            for doc in saved_documents:
                upsert_document_record(self, doc, property_uid)
    
            self.db.commit()
    
            return {
                "success": True,
                "message": "Survey submitted successfully.",
                "property_uid": property_uid,
                "survey_id": survey["survey_id"],
                "is_resurvey": is_resurvey
            }
    
        except SQLAlchemyError:
            self.db.rollback()
            raise
    
        except Exception:
            self.db.rollback()
            raise
 
    # Save Bulk Surveys In json Format
    def save_bulk_surveys(self, payloads):
        if not isinstance(payloads, list):
            payloads = [payloads]

        results = []
        success_count = 0
        failure_count = 0

        for index, payload in enumerate(payloads, start=1):
            try:
                result = self.save_complete_survey(payload)
                success_count += 1
                results.append({
                    "index": index,
                    "success": True,
                    "result": result,
                })
            except Exception as exc:
                failure_count += 1
                results.append({
                    "index": index,
                    "success": False,
                    "error": str(exc),
                })

        return {
            "success": True,
            "message": "Bulk survey sync completed.",
            "total": len(payloads),
            "saved": success_count,
            "failed": failure_count,
            "results": results,
        }


    # Save Data Comes From Multi Part Form Data
    def submit_survey_form(self, payload: dict):
        payload = to_dict(payload)

        if not to_dict(payload.get("survey_information")):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="survey_information is required.",
            )

        return self.save_complete_survey(payload, files_are_uploads=True)

    # Get Completed Survey Data In Summary By Surveyor ID
    def get_completed_survey_data(self, surveyor_id: str):
        try:
            survey_rows = (
                self.db.query(
                    SurveyInformation.parcel_no,
                    SurveyInformation.property_uid,
                    SurveyInformation.survey_id,
                    SurveyInformation.surveyor_name,
                    SurveyInformation.surveyor_id,
                    SurveyInformation.zone,
                    SurveyInformation.survey_date,
                )
                .filter(SurveyInformation.surveyor_id == surveyor_id)
                .all()
            )

            surveys = {
                row.survey_id: {
                    "parcel_no": row.parcel_no,
                    "property_uid": row.property_uid,
                    "survey_id": row.survey_id,
                    "surveyor_name": row.surveyor_name,
                    "surveyor_id": row.surveyor_id,
                    "zone": row.zone,
                    "survey_date": row.survey_date,
                }
                for row in survey_rows
            }
            return {
                "success": True,
                "surveyor_id": surveyor_id,
                "total_surveys": len(surveys),
                "surveys": surveys,
            }

        except Exception as e:
            self.db.rollback()
            raise e

    # Get Details of Survey Data By Survey ID
    def get_survey_data_by_survey_id(self, survey_id: str):
        try:
            survey_info = (
                self.db.query(SurveyInformation)
                .filter(SurveyInformation.survey_id == survey_id)
                .first()
            )

            if not survey_info:
                return {
                    "success": False,
                    "message": "Survey not found."
                }

            property_uid = survey_info.property_uid
            property_id = survey_info.property_id

            survey = {}

            # Fetch all mapped sections
            for section, model in MODEL_MAPPING.items():

                if model is SurveyInformation:
                    data = survey_info

                elif hasattr(model, "property_uid"):
                    data = (
                        self.db.query(model)
                        .filter(model.property_uid == property_uid)
                        .first()
                    )

                elif hasattr(model, "property_id"):
                    data = (
                        self.db.query(model)
                        .filter(model.property_id == property_id)
                        .first()
                    )

                else:
                    data = None

                if data:
                    survey[section] = {
                        column.name: getattr(data, column.name)
                        for column in data.__table__.columns
                    }

            # Fetch Land Building Areas
            land_building_areas = (
                self.db.query(LandBuildingArea)
                .filter(LandBuildingArea.property_uid == property_uid)
                .order_by(
                    LandBuildingArea.area_type,
                )
                .all()
            )

            if land_building_areas:
                survey["floor_details"] = [
                    {
                        "floor": area.level_name,
                        "area": area.area,
                        "usage_factor": area.usage_factor,
                        "usage_type": area.usage_type,
                        "construction_type": area.construction_type,
                        "roof_type": area.roof_type,
                    }
                    for area in land_building_areas
                ]

            # Fetch Documents
            documents = (
                self.db.query(DocumentsCollected)
                .filter(DocumentsCollected.property_uid == property_uid)
                .all()
            )

            if documents:
                survey["documents_collected"] = [
                    {
                        column.name: getattr(doc, column.name)
                        for column in doc.__table__.columns
                    }
                    for doc in documents
                ]

            return {
                "success": True,
                "survey": survey
            }
        except Exception as e:
                self.db.rollback()
                raise e



    # Get All Survey Documents
    def get_all_survey_documents(self):
        try:
            documents = self.db.query(DocumentsCollected).all()
            return documents
        except Exception as e:
            self.db.rollback()
            raise e

    # Get List Of Existing Property IDs
    def get_existing_property_ids(self):
        try:
            results = (
                self.db.query(
                    ParcelMaster.existing_property_id,
                    OwnerDetails.owner_name,
                    OwnerDetails.mobile_number,
                )
                .join(
                    OwnerDetails,
                    ParcelMaster.property_uid == OwnerDetails.property_uid,
                )
                .filter(
                ParcelMaster.is_active.is_(True),
                ParcelMaster.existing_property_id.is_not(None),
                ParcelMaster.existing_property_id != ""
            )
                .all()
            )

            return [
                {
                    "existing_property_id": row.existing_property_id,
                    "owner_name": row.owner_name,
                    "mobile_number": row.mobile_number,
                }
                for row in results
            ]

        except Exception:
            self.db.rollback()
            raise
        
    # Get All Table Data  Exist Corresponding to existing Property IDs
    def get_survey_data_by_existing_property_id(self, property_ids):
        try:
            if not property_ids:
                return {}

            all_data = {}
          
            property_uids = (
                self.db.query(ParcelMaster.property_uid)
                .filter(
                    or_(
                        ParcelMaster.property_id.in_(property_ids),
                        ParcelMaster.existing_property_id.in_(property_ids),
                        ParcelMaster.parcel_no.in_(property_ids),
                    )
                )
                .all()
            )
            property_uids = [pu[0] for pu in property_uids]
            
            
            for section, model in MODEL_MAPPING.items():
                if hasattr(model, "property_uid"):
                    row = (
                        self.db.query(model)
                        .filter(model.property_uid.in_(property_uids))
                        .first()
                    )

                    all_data[section] = (
                        {column.name: getattr(row, column.name) for column in row.__table__.columns}
                        if row
                        else {}
                    )
            return all_data
        
        except Exception as e:
            self.db.rollback()
            raise e
    
