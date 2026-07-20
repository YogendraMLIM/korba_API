from pydantic import BaseModel

from schema.survey_information import SurveyInformationCreate
from schema.owner_details import OwnerDetailsCreate
from schema.occupier_details import OccupierDetailsCreate
from schema.property_details import PropertyDetailsCreate
from schema.land_building_information import LandBuildingInformationCreate
from schema.usage_details import UsageDetailsCreate
from schema.tax_related_information import TaxRelatedInformationCreate
from schema.utility_connections import UtilityConnectionsCreate
from schema.gis_information import GISInformationCreate
from schema.smart_addressing import SmartAddressingCreate
from schema.verification import VerificationCreate
from schema.documents_collected import DocumentsCollectedCreate
from schema.surveyor_remarks import SurveyorRemarksCreate
from schema.owner_declaration import OwnerDeclarationCreate


class SurveyRequest(BaseModel):

    survey_information: SurveyInformationCreate

    owner_details: OwnerDetailsCreate | None = None

    occupier_details: OccupierDetailsCreate | None = None

    property_details: PropertyDetailsCreate | None = None

    land_building_information: LandBuildingInformationCreate | None = None

    usage_details: UsageDetailsCreate | None = None

    tax_related_information: TaxRelatedInformationCreate | None = None

    utility_connections: UtilityConnectionsCreate | None = None

    gis_information: GISInformationCreate | None = None

    smart_addressing: SmartAddressingCreate | None = None

    verification: VerificationCreate | None = None

    documents_collected: DocumentsCollectedCreate | None = None

    surveyor_remarks: SurveyorRemarksCreate | None = None

    # owner_declaration: OwnerDeclarationCreate | None = None