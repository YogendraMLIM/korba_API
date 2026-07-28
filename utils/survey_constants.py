from datetime import date, datetime

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
        "survey_date": datetime.now(),
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

