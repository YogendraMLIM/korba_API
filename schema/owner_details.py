import re

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


NAME_PATTERN = r"^[A-Za-z .'-]+$"
MOBILE_PATTERN = r"^[6-9]\d{9}$"
AADHAAR_PATTERN = r"^\d{12}$"


class OwnerDetailsBase(BaseModel):

   
    owner_name: str = Field(..., max_length=200)

    father_husband_name: str = Field(..., max_length=200)

    mobile_number: str = Field(..., min_length=10, max_length=10)

    alternate_mobile: str | None = Field(
        default=None,
        min_length=10,
        max_length=10
    )

    aadhaar_no: str | None = Field(
        default=None,
        min_length=12,
        max_length=12
    )

    email: EmailStr | None = None

    correspondence_address: str = Field(
        ...,
        max_length=500
    )

    @field_validator("owner_name", "father_husband_name")
    @classmethod
    def validate_names(cls, value):
        if not re.fullmatch(NAME_PATTERN, value):
            raise ValueError(
                "Only alphabets, spaces, '.', '-', and apostrophe are allowed."
            )
        return value

    @field_validator("mobile_number", "alternate_mobile")
    @classmethod
    def validate_mobile(cls, value):
        if value is None:
            return value

        if not re.fullmatch(MOBILE_PATTERN, value):
            raise ValueError("Invalid Indian mobile number.")
        return value

    @field_validator("aadhaar_no")
    @classmethod
    def validate_aadhaar(cls, value):
        if value is None:
            return value

        if not re.fullmatch(AADHAAR_PATTERN, value):
            raise ValueError("Aadhaar must contain exactly 12 digits.")
        return value


class OwnerDetailsCreate(OwnerDetailsBase):
    pass


class OwnerDetailsUpdate(BaseModel):

    owner_name: str | None = None
    father_husband_name: str | None = None
    mobile_number: str | None = None
    alternate_mobile: str | None = None
    aadhaar_no: str | None = None
    email: EmailStr | None = None
    correspondence_address: str | None = None


class OwnerDetailsResponse(OwnerDetailsBase):

    id: int

    model_config = ConfigDict(from_attributes=True)