from pydantic import BaseModel, Field


class ApiConfig(BaseModel):
    base_url: str
    api_key_env: str
    rate_limit_qps: int = Field(gt=0)
    daily_call_cap: int = Field(gt=0)
    retry_max_attempts: int = Field(ge=1)
    retry_backoff_base: float = Field(gt=0)
    request_timeout_seconds: int = Field(gt=0)
