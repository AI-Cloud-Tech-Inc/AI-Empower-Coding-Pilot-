"""Application configuration via environment variables."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from environment / .env file."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # LLM
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="Default LLM model")
    openai_temperature: float = Field(default=0.1)

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/app.db",
        description="Async database connection string",
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Vector store
    chroma_persist_dir: str = Field(default="./data/chroma")
    embedding_model: str = Field(default="text-embedding-3-small")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_secret_key: str = Field(default="change-me-in-production")
    api_cors_origins: list[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])

    # JWT Auth
    jwt_secret_key: str = Field(default="change-jwt-secret-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=60)

    # Compliance
    compliance_enabled: bool = Field(default=True)
    hipaa_enabled: bool = Field(default=True)
    pci_enabled: bool = Field(default=True)
    soc2_enabled: bool = Field(default=True)
    gdpr_enabled: bool = Field(default=True)

    # Audit
    audit_log_level: str = Field(default="INFO")
    audit_log_file: str = Field(default="./logs/audit.log")

    # Cost
    max_tokens_per_request: int = Field(default=4096)
    max_cost_per_project: float = Field(default=50.00)
    cost_alert_threshold: float = Field(default=0.80)

    # Agents
    max_parallel_agents: int = Field(default=4)
    agent_timeout_seconds: int = Field(default=300)


settings = Settings()
