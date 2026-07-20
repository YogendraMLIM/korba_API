from pydantic import BaseModel, ConfigDict, Field


class DocumentsCollectedBase(BaseModel):

   

    aadhaar_copy: str | None = None

    electricity_bill: str | None = None

    water_bill: str | None = None

    sale_deed: str | None = None

    property_tax_receipt: str | None = None

    building_permission: str | None = None

    other_documents: str | None = Field(
        default=None,
        max_length=500
    )


class DocumentsCollectedCreate(DocumentsCollectedBase):
    pass


class DocumentsCollectedUpdate(BaseModel):

    aadhaar_copy: str | None = None
    electricity_bill: str | None = None
    water_bill: str | None = None
    sale_deed: str | None = None
    property_tax_receipt: str | None = None
    building_permission: str | None = None
    other_documents: str | None = None


class DocumentsCollectedResponse(
    DocumentsCollectedBase
):
    id: int

    model_config = ConfigDict(from_attributes=True)