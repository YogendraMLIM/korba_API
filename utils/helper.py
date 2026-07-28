from datetime import date, datetime

from nanoid import generate
from sqlalchemy import or_
from sqlalchemy.orm import Session
import json
import re
from typing import Any, Dict, List
from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request, status
from sqlalchemy.inspection import inspect
from models.documents_collected import DocumentsCollected
from models.land_building_area import LandBuildingArea
from models.parcel_master import ParcelMaster
# from services.survey_service import  SurveyService
from services.upload_service import DOCUMENT_FIELDS
from utils.survey_constants import (
    MODEL_MAPPING,
    MODEL_DEFAULTS,
)
# from utils.helper import (
#     _apply_model_defaults,
#     _coerce_by_column,
#     _field_parts,
#     _find_existing_parcel_for_survey,
#     _first_item,
#     _parse_bool,
#     _parse_date,
#     _parse_datetime,
#     _sanitize_for_model,
#     _set_nested_value,
#     _to_dict,
#     _to_str_or_none,

# Helper functions for processing survey form data and files
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


def build_flat_field_sections() -> dict[str, str]:
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


FLAT_FIELD_SECTIONS = build_flat_field_sections()


def parse_form_value(value: Any):
    if not isinstance(value, str):
        return value

    text = value.strip()
    if text == "":
        return ""

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return value


def field_parts(field_name: str) -> list[str]:
    normalized = re.sub(r"\[([^\]]+)\]", r".\1", field_name)
    parts = [part for part in normalized.split(".") if part]

    if parts and parts[0] in {"payload", "data", "survey_data"}:
        parts = parts[1:]
    if parts and parts[0] == "gis_info":
        parts[0] = "gis_information"

    return parts


def set_nested_value(payload: dict, field_name: str, value: Any):
    parts = field_parts(field_name)
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
def append_file(
    payload: dict,
    field_name: str,
    file_data: dict,
    filename: str | None = None,
):
    parts = field_parts(field_name)
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
async def multipart_to_survey_payload(request: Request) -> dict:
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
            append_file(payload, key, file_data, value.filename)
            continue

        parsed_value =  parse_form_value(value)

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

        set_nested_value(payload, key, parsed_value)

    return payload


# Helper Function to Save Survey Data to the Database
def to_dict(value):
    return value if isinstance(value, dict) else {}

def to_str_or_none(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None

def first_item(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value

def first_present(*values):
    for value in values:
        if value not in (None, ""):
            return value
    return None

def parse_bool(value):
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

def parse_datetime(value):
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

def parse_date(value):
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

def coerce_by_column(value, column):
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
            return parse_bool(value)

        if "datetime" in type_name:
            return parse_datetime(value)

        if type_name == "date":
            return parse_date(value)

        if "string" in type_name or "varchar" in type_name or "text" in type_name:
            if value is None:
                return None
            return str(value)

        return value

    except Exception:
        return None

def sanitize_for_model( model, section_data):
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
        clean_data[key] = coerce_by_column(raw_value, column)

    return clean_data


def apply_model_defaults( model, section_data):
    for key, default in MODEL_DEFAULTS.get(model, {}).items():
        if section_data.get(key) is None:
            section_data[key] = default() if callable(default) else default
    return section_data

# Find Existing Parcel For Survey using property_uid, existing_property_id, property_id, or parcel_no
def find_existing_parcel_for_survey(self, survey: dict):
    property_uid = to_str_or_none(survey.get("property_uid"))
    existing_property_id = to_str_or_none(survey.get("existing_property_id"))
    property_id = to_str_or_none(survey.get("property_id"))
    parcel_no = to_str_or_none(survey.get("parcel_no"))

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
def upsert_by_property_uid(self, model, section_data: dict):
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
def upsert_land_building_area(self, area_row: dict):
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


# Extract Land and Building Areas from Survey Data`
def extract_land_building_areas(
    self,
    section_data: dict,
    property_uid: str,
    surveyor_id: str | None,
):
    detailed_floor_value = first_present(
        # section_data.get("floor_details"),
        section_data.get("floor_detail")
        # section_data.get("floorDetail"),
    )
    floor_areas = normalize_area_collection(
        first_present(detailed_floor_value, section_data.get("floor_areas"))
    )
    basement_areas = normalize_area_collection(
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
        if value not in (None, "") and str(level_no) not in floor_areas:
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
            floor_areas.setdefault(floor_match.group(1), value)
            continue

        basement_match = (
            re.fullmatch(r"basement_area_(\d+)", key)
            or re.fullmatch(r"basementArea(\d+)", key)
        )

        if basement_match:
            basement_areas[basement_match.group(1)] = value

    return (
        build_area_rows(
            area_type="floor",
            areas=floor_areas,
            property_uid=property_uid,
            surveyor_id=surveyor_id
        )
        + build_area_rows(
            area_type="basement",
            areas=basement_areas,
            property_uid=property_uid,
            surveyor_id=surveyor_id
        )
    )

# Normalize Area Collection
def normalize_area_collection(value):
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
def build_area_rows(
    area_type: str,
    areas: dict,
    property_uid: str,
    surveyor_id: str,
):
    rows = []

    for level, value in areas.items():
        area = value
        level_name = None
        usage_factor = None
        usage_type = None
        construction_type = None
        roof_type = None

        if isinstance(value, dict):
            area = value.get("area")
            level_value = first_present(value.get("level_no"), value.get("level"))
            level_name = first_present(
                value.get("level_name"),
                value.get("floor_name"),
                value.get("floor"),
            )
            usage_factor = first_present(
                value.get("usage_factor"),
                value.get("usage_facotor"),
            )
            usage_type = value.get("usage_type")
            construction_type = value.get("construction_type")
            roof_type = value.get("roof_type")
        else:
            level_value = level

        if area in (None, ""):
            continue

        level_no = level_to_int(level_value) if level_value is not None else None

        area_column = inspect(LandBuildingArea).mapper.columns.get("area")
        normalized_area = coerce_by_column(area, area_column)
        if normalized_area is None:
            continue
        usage_factor_column = inspect(LandBuildingArea).mapper.columns.get("usage_factor")
        usage_type_column = inspect(LandBuildingArea).mapper.columns.get("usage_type")
        construction_type_column = inspect(LandBuildingArea).mapper.columns.get("construction_type")
        roof_type_column = inspect(LandBuildingArea).mapper.columns.get("roof_type")

        rows.append({
            "property_uid": property_uid,
            "surveyor_id": surveyor_id,
            "area_type": area_type,
            "level_no": level_no,
            "level_name": level_name,
            "area": normalized_area,
            "usage_factor": coerce_by_column(usage_factor, usage_factor_column),
            "usage_type": coerce_by_column(usage_type, usage_type_column),
            "construction_type": coerce_by_column(construction_type, construction_type_column),
            "roof_type": coerce_by_column(roof_type, roof_type_column),
        })

    return rows

# Convert Level to Integer
def level_to_int(value):
    text = str(value).strip().lower()
    if text in {"ground", "ground floor", "gf", "g"}:
        return 0

    named_levels = {
        "first": 1,
        "first floor": 1,
        "1st": 1,
        "1st floor": 1,
        "second": 2,
        "second floor": 2,
        "2nd": 2,
        "2nd floor": 2,
        "third": 3,
        "third floor": 3,
        "3rd": 3,
        "3rd floor": 3,
    }
    if text in named_levels:
        return named_levels[text]

    floor_match = re.fullmatch(r"(\d+)(?:st|nd|rd|th)?\s*floor", text)
    if floor_match:
        return int(floor_match.group(1))

    try:
        return int(float(text))
    except (TypeError, ValueError):
        return None
    

#  Save Document Records
def upsert_document_record(self, document: dict, property_uid: str):
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
    

def repoint_property_uid(self, old_property_uid: str, new_property_uid: str):
    if not old_property_uid or old_property_uid == new_property_uid:
        return
 
    # Child rows are updated by ON UPDATE CASCADE foreign keys.
    self.db.query(ParcelMaster).filter(
        ParcelMaster.property_uid == old_property_uid
    ).update({"property_uid": new_property_uid}, synchronize_session=False)
 
    self.db.flush()
 
