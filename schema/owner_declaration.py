from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class OwnerDeclarationBase(BaseModel):

  

    owner_declaration_accepted: bool

    owner_signature: str | None = None

    owner_refusal_reason: str | None = Field(
        default=None,
        max_length=500
    )

    surveyor_signature: str

    declaration_date: datetime | None = None

    @model_validator(mode="after")
    def validate_declaration(self):

        if not self.owner_declaration_accepted:
            raise ValueError(
                "Owner declaration must be accepted before survey submission."
            )

        if (
            self.owner_signature is None
            and self.owner_refusal_reason is None
        ):
            raise ValueError(
                "Owner signature or refusal reason is required."
            )

        return self


class OwnerDeclarationCreate(OwnerDeclarationBase):
    pass


class OwnerDeclarationUpdate(BaseModel):

    owner_declaration_accepted: bool | None = None

    owner_signature: str | None = None

    owner_refusal_reason: str | None = None

    surveyor_signature: str | None = None


class OwnerDeclarationResponse(OwnerDeclarationBase):

    id: int

    declaration_date: datetime

    model_config = ConfigDict(
        from_attributes=True
    )