from pydantic import BaseModel, Field, ConfigDict


class FieldValue(BaseModel):
    value: str | None = None


def default_field_value() -> list[FieldValue]:
    return [FieldValue()]


class NimbleFields(BaseModel):
    first_name: list[FieldValue] = Field(
        default_factory=default_field_value,
        alias="first name",
    )
    last_name: list[FieldValue] = Field(
        default_factory=default_field_value,
        alias="last name",
    )
    email: list[FieldValue] = Field(default_factory=default_field_value)
    description: list[FieldValue] = Field(default_factory=default_field_value)

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
    )


class NimbleResource(BaseModel):
    record_type: str
    fields: NimbleFields
    id: str


class NimbleMeta(BaseModel):
    page: int
    pages: int
    per_page: int
    total: int


class NimbleResponse(BaseModel):
    resources: list[NimbleResource] = Field(default_factory=list)
    meta: NimbleMeta


class ContactBase(BaseModel):
    first_name: str | None = Field(
        validation_alias="first name",
        serialization_alias="first name",
    )
    last_name: str | None = Field(
        validation_alias="last name",
        serialization_alias="last name",
    )
    email: str | None = None
    description: str | None = None


class ContactNimble(ContactBase):
    nimble_id: str

    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
    )


class ContactSchema(ContactNimble):
    id: int
    nimble_id: str | None = None
    model_config = ConfigDict(from_attributes=True)
