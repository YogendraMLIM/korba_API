from pydantic import BaseModel, ConfigDict, Field


class SurveyorRemarksBase(BaseModel):


    surveyor_remarks: str | None = None

    supervisor_remarks: str | None = None


class SurveyorRemarksCreate(SurveyorRemarksBase):
    pass


class SurveyorRemarksUpdate(BaseModel):

    surveyor_remarks: str | None = None

    supervisor_remarks: str | None = None


class SurveyorRemarksResponse(SurveyorRemarksBase):

    id: int

    model_config = ConfigDict(from_attributes=True)