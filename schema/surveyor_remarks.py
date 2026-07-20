from pydantic import BaseModel, ConfigDict, Field


class SurveyorRemarksBase(BaseModel):


    surveyor_remarks: str | None = Field(
        default=None,
        max_length=1000
    )

    supervisor_remarks: str | None = Field(
        default=None,
        max_length=1000
    )


class SurveyorRemarksCreate(SurveyorRemarksBase):
    pass


class SurveyorRemarksUpdate(BaseModel):

    surveyor_remarks: str | None = Field(
        default=None,
        max_length=1000
    )

    supervisor_remarks: str | None = Field(
        default=None,
        max_length=1000
    )


class SurveyorRemarksResponse(SurveyorRemarksBase):

    id: int

    model_config = ConfigDict(from_attributes=True)