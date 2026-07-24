from pydantic import BaseModel, Field, ConfigDict


class DocumentsCollectedCreate(BaseModel):
    aadhaar_copy: str | None = None
    electricity_bill: str | None = None
    water_bill: str | None = None
    sale_deed: str | None = None
    property_tax_receipt: str | None = None
    building_permission: str | None = None
    other_documents: str | None = None

    aadhaar_copy_files: list[str] | None = None
    electricity_bill_files: list[str] | None = None
    water_bill_files: list[str] | None = None
    sale_deed_files: list[str] | None = None
    property_tax_receipt_files: list[str] | None = None
    building_permission_files: list[str] | None = None
    other_documents_files: list[str] | None = None


class DocumentsCollectedUpdate(BaseModel):
    aadhaar_copy: str | None = None
    electricity_bill: str | None = None
    water_bill: str | None = None
    sale_deed: str | None = None
    property_tax_receipt: str | None = None
    building_permission: str | None = None
    other_documents: str | None = None

    aadhaar_copy_files: list[str] | None = None
    electricity_bill_files: list[str] | None = None
    water_bill_files: list[str] | None = None
    sale_deed_files: list[str] | None = None
    property_tax_receipt_files: list[str] | None = None
    building_permission_files: list[str] | None = None
    other_documents_files: list[str] | None = None


class DocumentRecord(BaseModel):
    id: int
    property_uid: str
    document_type: str
    file_path: str

    model_config = ConfigDict(from_attributes=True)


class DocumentsCollectedResponse(BaseModel):
    documents: list[DocumentRecord]

    model_config = ConfigDict(from_attributes=True)