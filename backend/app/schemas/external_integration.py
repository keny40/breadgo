from pydantic import BaseModel, ConfigDict


class ExternalIntegrationReadinessItemRead(BaseModel):
    area: str
    provider: str
    status: str
    mode: str
    external_calls_enabled: bool
    message: str

    model_config = ConfigDict(from_attributes=True)


class ExternalIntegrationDryRunItemRead(BaseModel):
    area: str
    provider: str
    status: str
    external_calls_enabled: bool
    message: str

    model_config = ConfigDict(from_attributes=True)


class ExternalIntegrationReadinessRead(BaseModel):
    overall_status: str
    external_calls_enabled: bool
    message: str
    items: list[ExternalIntegrationReadinessItemRead]
    dry_runs: list[ExternalIntegrationDryRunItemRead]

    model_config = ConfigDict(from_attributes=True)
