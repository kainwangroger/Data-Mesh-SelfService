"""
Pydantic schemas for the Governance API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DataProductCreate(BaseModel):
    name: str
    domain: str
    description: Optional[str] = ""
    owner: str
    input_ports: list = []
    output_ports: list = []
    sla_tier: str = "silver"
    tags: list = []


class DataProductResponse(DataProductCreate):
    id: int
    version: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataContractCreate(BaseModel):
    name: str
    provider_domain: str
    consumer_domain: str
    data_product_name: str
    sla: dict = {}
    terms: dict = {}


class DataContractResponse(DataContractCreate):
    id: int
    schema_version: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    policy_type: str
    rule: dict
    effect: str = "deny"
    priority: int = 0


class PolicyResponse(PolicyCreate):
    id: int
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DomainCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    owner: Optional[str] = None
    database: Optional[str] = None
    storage_quota_gb: float = 10.0


class DomainResponse(DomainCreate):
    id: int
    schema_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
