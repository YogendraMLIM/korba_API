from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class OwnerDeclarationBase(BaseModel):

  

    owner_declaration_accepted: bool

    owner_signature: str | None = None

    owner_refusal_reason: str | None = None

    surveyor_signature: str

    declaration_date: datetime | None = None


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