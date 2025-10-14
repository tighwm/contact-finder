from pydantic import BaseModel, Field


class FieldValue(BaseModel):
    value: str


class ContactFields(BaseModel):
    first_name: list[FieldValue] | None = Field(alias="first name")
    last_name: list[FieldValue] | None = Field(alias="last name")
    email: list[FieldValue] | None
    description: list[FieldValue] | None


class ContactResource(BaseModel):
    record_type: str
    fields: ContactFields


class ContactResponse(BaseModel):
    resources: list[ContactResource]
