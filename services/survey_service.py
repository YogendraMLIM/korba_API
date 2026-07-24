import re
from datetime import date, datetime

from utils.helper import generate_unique_id
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

MODEL_DEFAULTS = {
    SurveyInformation: {
        "property_location": "Unknown",
        "survey_date": datetime.now,
        "surveyor_name": "",
        "ward_no": 1,
        "zone": "",
        "colony_locality": "",
        "gps_latitude": 0,
        "gps_longitude": 0,
    },
    OwnerDetails: {
        "mobile_number": "",
        "correspondence_address": "",
    },
    OccupierDetails: {
        "occupancy_status": "",
    },
    PropertyDetails: {
        "property_type": "",
        "property_status": "",
        "building_permission_available": False,
        "property_ownership": "",
    },
    LandBuildingInformation: {
        "plot_area": 0,
        "total_builtup_area": 0,
        "number_of_floors": 0,
        "construction_type": "",
        "roof_type": "",
    },
    UsageDetails: {
        "primary_use": "",
        "mixed_use": False,
        "occupancy": "",
        "number_of_families": 0,
        "number_of_shops": 0,
    },
    TaxRelatedInformation: {
        "outstanding_tax": 0,
        "exempted_property": False,
    },
    UtilityConnections: {
        "sewer_connection": False,
        "gas_connection": False,
    },
    GISInformation: {
        "gis_property_polygon_available": False,
        "property_boundary_verified": False,
        "geo_tag_completed": False,
        "property_photo_captured": False,
        "front_elevation_photo": False,
        "name_plate_photo": False,
    },
    Verification: {
        "unassessed_property": False,
        "under_assessed_property": False,
        "property_use_changed": False,
        "additional_floor_constructed": False,
        "boundary_changed": False,
        "ownership_changed": False,
        "demolished_property": False,
        "new_property": False,
    },
}


class SurveyService:

    def __init__(self, db: Session):
        self.db = db

    def _to_dict(self, value):
        return value if isinstance(value, dict) else {}

    def _to_str_or_none(self, value):
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _first_item(self, value):
        if isinstance(value, list):
            return value[0] if value else None
        return value

    def _parse_bool(self, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value != 0

        text = str(value).strip().lower()
        if text in {"true", "1", "yes", "y", "on"}:
            return True
        if text in {"false", "0", "no", "n", "off"}:
            return False
        return None

    def _parse_datetime(self, value):
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value

        text = str(value).strip()
        if text.endswith("Z"):
            text = text[:-1]

        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y, %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(text)
        except ValueError:
            return None

    def _parse_date(self, value):
        if value in (None, ""):
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()

        text = str(value).strip()
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]

        for fmt in formats:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue

        return None

    def _coerce_by_column(self, value, column):
        if value in ("",):
            return None

        if column is None:
            return value

        type_name = column.type.__class__.__name__.lower()

        try:
            if "integer" in type_name:
                if value is None:
                    return None
                return int(float(value))

            if any(token in type_name for token in ["numeric", "float", "double", "decimal", "real"]):
                if value is None:
                    return None
                return float(str(value).replace(",", ""))

            if "boolean" in type_name:
                return self._parse_bool(value)

            if "datetime" in type_name:
                return self._parse_datetime(value)

            if type_name == "date":
                return self._parse_date(value)

            if "string" in type_name or "varchar" in type_name or "text" in type_name:
                if value is None:
                    return None
                return str(value)

            return value

        except Exception:
            return None

    def _sanitize_for_model(self, model, section_data):
        if not isinstance(section_data, dict):
            return {}

        columns = {
            attr.key: attr.columns[0]
            for attr in inspect(model).mapper.column_attrs
        }

        clean_data = {}
        for key, raw_value in section_data.items():
            column = columns.get(key)
            if column is None:
                continue
            clean_data[key] = self._coerce_by_column(raw_value, column)

        return clean_data


    def _apply_model_defaults(self, model, section_data):
        for key, default in MODEL_DEFAULTS.get(model, {}).items():
            if section_data.get(key) is None:
                section_data[key] = default() if callable(default) else default
        return section_data

    # Find Existing Parcel For Survey using property_uid, existing_property_id, property_id, or parcel_no
    def _find_existing_parcel_for_survey(self, survey: dict):
        property_uid = self._to_str_or_none(survey.get("property_uid"))
        existing_property_id = self._to_str_or_none(survey.get("existing_property_id"))
        property_id = self._to_str_or_none(survey.get("property_id"))
        parcel_no = self._to_str_or_none(survey.get("parcel_no"))

        if property_uid:
            parcel = (
                self.db.query(ParcelMaster)
                .filter(ParcelMaster.property_uid == property_uid)
                .first()
            )
            if parcel:
                return parcel

        property_candidates = [
            value for value in [existing_property_id, property_id, parcel_no] if value
        ]
        if not property_candidates:
            return None

        return (
            self.db.query(ParcelMaster)
            .filter(
                or_(
                    ParcelMaster.existing_property_id.in_(property_candidates),
                    ParcelMaster.property_id.in_(property_candidates),
                    ParcelMaster.parcel_no.in_(property_candidates),
                )
            )
            .first()
        )

    #  Insert Record By Property UID
    def _upsert_by_property_uid(self, model, section_data: dict):
        property_uid = section_data.get("property_uid")
        existing_obj = (
            self.db.query(model)
            .filter(model.property_uid == property_uid)
            .first()
        )

        if not existing_obj:
            obj = model(**section_data)
            self.db.add(obj)
            return obj

        primary_key_names = {
            column.key for column in inspect(model).primary_key
        }
        for key, value in section_data.items():
            if key not in primary_key_names:
                setattr(existing_obj, key, value)
        return existing_obj

    #  Save Land Building Area Records
    def _upsert_land_building_area(self, area_row: dict):
        existing_obj = (
            self.db.query(LandBuildingArea)
            .filter(
                LandBuildingArea.property_uid == area_row.get("property_uid"),
                LandBuildingArea.area_type == area_row.get("area_type"),
                LandBuildingArea.level_no == area_row.get("level_no"),
            )
            .first()
        )

        if not existing_obj:
            obj = LandBuildingArea(**area_row)
            self.db.add(obj)
            return obj

        for key, value in area_row.items():
            if key != "id":
                setattr(existing_obj, key, value)
        return existing_obj

    #  Save Document Records
    def _upsert_document_record(self, document: dict, property_uid: str):
        existing_obj = (
            self.db.query(DocumentsCollected)
            .filter(
                DocumentsCollected.property_uid == property_uid,
                DocumentsCollected.document_type == document["document_type"],
                DocumentsCollected.file_path == document["file_path"],
            )
            .first()
        )

        if existing_obj:
            return existing_obj

        obj = DocumentsCollected(
            property_uid=property_uid,
            document_type=document["document_type"],
            file_path=document["file_path"]
        )
        self.db.add(obj)
        return obj
      

   # Extract Land and Building Areas from Survey Data`
    def _extract_land_building_areas(
        self,
        section_data: dict,
        property_uid: str,
        surveyor_id: str | None,
    ):
        floor_areas = self._normalize_area_collection(
            section_data.get("floor_areas")
        )
        basement_areas = self._normalize_area_collection(
            section_data.get("basement_areas")
        )

        if not surveyor_id:
            return []

        fixed_floor_fields = {
            "ground_floor_area": (0, "ground"),
            "first_floor_area": (1, "first"),
            "second_floor_area": (2, "second"),
            "third_floor_area": (3, "third"),
        }

        for field, (level_no, level_name) in fixed_floor_fields.items():
            value = section_data.get(field)
            if value not in (None, ""):
                floor_areas[str(level_no)] = {
                    "area": value,
                    "level_name": level_name
                }

        for key, value in list(section_data.items()):
            if value in (None, ""):
                continue

            floor_match = (
                re.fullmatch(r"floor_area_(\d+)", key)
                or re.fullmatch(r"floor_(\d+)_area", key)
                or re.fullmatch(r"floorArea(\d+)", key)
                or re.fullmatch(r"floor(\d+)Area", key)
            )

            if floor_match:
                floor_areas[floor_match.group(1)] = value
                continue

            basement_match = (
                re.fullmatch(r"basement_area_(\d+)", key)
                or re.fullmatch(r"basementArea(\d+)", key)
            )

            if basement_match:
                basement_areas[basement_match.group(1)] = value

        return (
            self._build_area_rows(
                area_type="floor",
                areas=floor_areas,
                property_uid=property_uid,
                surveyor_id=surveyor_id
            )
            + self._build_area_rows(
                area_type="basement",
                areas=basement_areas,
                property_uid=property_uid,
                surveyor_id=surveyor_id
            )
        )

    # Normalize Area Collection
    def _normalize_area_collection(self, value):
        if isinstance(value, dict):
            return {
                str(key): area
                for key, area in value.items()
                if area not in (None, "")
            }

        if isinstance(value, list):
            return {
                str(index): area
                for index, area in enumerate(value, start=1)
                if area not in (None, "")
            }

        return {}

    # Build Area Rows for Land and Building Areas
    def _build_area_rows(
        self,
        area_type: str,
        areas: dict,
        property_uid: str,
        surveyor_id: str,
    ):
        rows = []

        for level, value in areas.items():
            area = value
            level_name = None

            if isinstance(value, dict):
                area = value.get("area")
                level_name = value.get("level_name")

            if area in (None, ""):
                continue

            level_no = self._level_to_int(level)
            if level_no is None:
                continue

            area_column = inspect(LandBuildingArea).mapper.columns.get("area")
            normalized_area = self._coerce_by_column(area, area_column)
            if normalized_area is None:
                continue

            rows.append({
                "property_uid": property_uid,
                "surveyor_id": surveyor_id,
                "area_type": area_type,
                "level_no": level_no,
                "level_name": level_name,
                "area": normalized_area,
            })

        return rows

    # Convert Level to Integer
    def _level_to_int(self, value):
        if str(value).lower() == "ground":
            return 0

        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None
        
        
    # Save Complete Survey In json Format  
    def save_complete_survey(self, payload: dict, files_are_uploads: bool = False):
        try:
            payload = self._to_dict(payload)
            survey = self._to_dict(payload.get("survey_information"))
            payload["survey_information"] = survey

            parcel_no = self._to_str_or_none(survey.get("parcel_no"))
            property_id = self._to_str_or_none(survey.get("property_id"))
            existing_parcel = self._find_existing_parcel_for_survey(survey)

            if existing_parcel:
                property_uid = existing_parcel.property_uid
                parcel_no = parcel_no or existing_parcel.parcel_no
                property_id = property_id or existing_parcel.property_id
            elif parcel_no and property_id:
                property_uid = f"{parcel_no}{property_id}"
            else:
                property_uid = self._to_str_or_none(survey.get("property_uid"))
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

            # Generate Survey ID
            existing_survey = (
                self.db.query(SurveyInformation)
                .filter(SurveyInformation.property_uid == property_uid)
                .first()
            )
            if existing_survey and not self._to_str_or_none(survey.get("survey_id")):
                survey["survey_id"] = existing_survey.survey_id
            elif not self._to_str_or_none(survey.get("survey_id")):
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
            documents_collected = self._to_dict(payload.get("documents_collected"))
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
            gis_info = self._to_dict(payload.get("gis_information"))

            if gis_info:
                if files_are_uploads:
                    property_photo_path = save_single_upload_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="property_photo",
                        upload=self._first_item(gis_info.get("property_photo_base64"))
                    )
                else:
                    property_photo_path = save_single_base64_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="property_photo",
                        file_data=self._first_item(gis_info.get("property_photo_base64"))
                    )
                if property_photo_path:
                    gis_info["property_photo_path"] = property_photo_path

                if files_are_uploads:
                    front_elevation_photo_path = save_single_upload_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="front_elevation_photo",
                        upload=self._first_item(gis_info.get("front_elevation_photo_base64"))
                    )
                else:
                    front_elevation_photo_path = save_single_base64_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="front_elevation_photo",
                        file_data=self._first_item(gis_info.get("front_elevation_photo_base64"))
                    )
                if front_elevation_photo_path:
                    gis_info["front_elevation_photo_path"] = front_elevation_photo_path

                if files_are_uploads:
                    name_plate_photo_path = save_single_upload_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="name_plate_photo",
                        upload=self._first_item(gis_info.get("name_plate_photo_base64"))
                    )
                else:
                    name_plate_photo_path = save_single_base64_image(
                        parcel_no=parcel_no,
                        property_id=property_id,
                        category="gis",
                        file_name="name_plate_photo",
                        file_data=self._first_item(gis_info.get("name_plate_photo_base64"))
                    )
                if name_plate_photo_path:
                    gis_info["name_plate_photo_path"] = name_plate_photo_path

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
                    property_id=property_id,
                    existing_property_id=survey.get("existing_property_id")
                )
                self.db.add(parcel)
                self.db.flush()
            else:
                parcel.parcel_no = parcel_no or parcel.parcel_no
                parcel.property_id = property_id or parcel.property_id
                parcel.existing_property_id = (
                    survey.get("existing_property_id")
                    or parcel.existing_property_id
                )

            # -----------------------------------
            # Save all sections
            # -----------------------------------
            land_building_area_rows = []

            for section, model in MODEL_MAPPING.items():

                if section == "documents_collected":
                    continue

                section_data = self._to_dict(payload.get(section))

                if not section_data:
                    continue

                section_data = dict(section_data)
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

                if model is LandBuildingInformation:
                    land_building_area_rows = self._extract_land_building_areas(
                        section_data=section_data,
                        property_uid=property_uid,
                        surveyor_id=survey.get("surveyor_id")
                    )

                section_data = self._sanitize_for_model(model, section_data)
                section_data = self._apply_model_defaults(model, section_data)

                self._upsert_by_property_uid(model, section_data)

            for area_row in land_building_area_rows:
                self._upsert_land_building_area(area_row)

            # -----------------------------------
            # Save Document Records
            # -----------------------------------
            for doc in saved_documents:
                self._upsert_document_record(doc, property_uid)

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
        payload = self._to_dict(payload)

        if not self._to_dict(payload.get("survey_information")):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="survey_information is required.",
            )

        return self.save_complete_survey(payload, files_are_uploads=True)

    # Get Completed Survey Data By Surveyor ID
    def get_completed_survey_data(self, surveyor_id: str):
        try:
            survey_rows = (
                self.db.query(SurveyInformation)
                .filter(SurveyInformation.surveyor_id == surveyor_id)
                .all()
            )

            surveys = []

            for survey_info in survey_rows:
                property_uid = survey_info.property_uid
                property_id = survey_info.property_id
                survey_obj = {}

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
                        survey_obj[section] = {
                            column.name: getattr(data, column.name)
                            for column in data.__table__.columns
                        }

                documents = (
                    self.db.query(DocumentsCollected)
                    .filter(DocumentsCollected.property_uid == property_uid)
                    .all()
                )
                if documents:
                    survey_obj["documents_collected"] = [
                        {
                            column.name: getattr(document, column.name)
                            for column in document.__table__.columns
                        }
                        for document in documents
                    ]

                surveys.append(survey_obj)

            return {
                "success": True,
                "count": len(surveys),
                "data": surveys
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
            existing_property_ids = (
                self.db.query(ParcelMaster.property_id)
                .filter(ParcelMaster.is_active == True)
                .all()
            )
            return [pid[0] for pid in existing_property_ids]
        except Exception as e:
            self.db.rollback()
            raise e
        
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
    
