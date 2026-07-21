from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class TaxRelatedInformationBase(BaseModel):


    existing_property_tax_no: str | None = Field(
        default=None,
        max_length=50
    )

    tax_paid_till: date | None = None

    outstanding_tax: float = Field(
        default=0,
        ge=0
    )
    
   

    exempted_property: bool

    exemption_category: Literal[
        "Government",
        "Religious",
        "Educational",
        "Other"
    ] | None = None

    @model_validator(mode="after")
    def validate_tax_information(self):

        if (
            self.tax_paid_till
            and self.tax_paid_till > date.today()
        ):
            raise ValueError(
                "Tax Paid Till cannot be a future date."
            )

        if (
            self.exempted_property
            and self.exemption_category is None
        ):
            raise ValueError(
                "Exemption Category is required."
            )

        return self


class TaxRelatedInformationCreate(
    TaxRelatedInformationBase
):
    pass


class TaxRelatedInformationUpdate(BaseModel):

    existing_property_tax_no: str | None = None

    tax_paid_till: date | None = None

    outstanding_tax: float | None = Field(
        default=None,
        ge=0
    )
    
  

    exempted_property: bool | None = None

    exemption_category: Literal[
        "Government",
        "Religious",
        "Educational",
        "Other"
    ] | None = None


class TaxRelatedInformationResponse(
    TaxRelatedInformationBase
):

    id: int

    model_config = ConfigDict(from_attributes=True)