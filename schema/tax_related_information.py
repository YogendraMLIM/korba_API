from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class TaxRelatedInformationBase(BaseModel):


    existing_property_tax_no: str | None = None

    tax_paid_till: date | None = None

    outstanding_tax: float | None = None
    
   

    exempted_property: bool 

    exemption_category: str | None = None


class TaxRelatedInformationCreate(
    TaxRelatedInformationBase
):
    pass


class TaxRelatedInformationUpdate(BaseModel):

    existing_property_tax_no: str | None = None

    tax_paid_till: date | None = None

    outstanding_tax: float | None = None
    
  

    exempted_property: bool | None = None

    exemption_category: str | None = None


class TaxRelatedInformationResponse(
    TaxRelatedInformationBase
):

    id: int

    model_config = ConfigDict(from_attributes=True)