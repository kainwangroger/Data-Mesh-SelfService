"""
SQLAlchemy models for the Governance Metadata Registry.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, JSON, Boolean, create_engine
)
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()


class DataProduct(Base):
    __tablename__ = "data_products"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    domain = Column(String(64), nullable=False)
    description = Column(Text)
    version = Column(String(8), default="1.0")
    owner = Column(String(64), nullable=False)
    input_ports = Column(JSON, default=list)
    output_ports = Column(JSON, default=list)
    sla_tier = Column(String(16), default="silver")
    schema_def = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    status = Column(String(16), default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class DataContract(Base):
    __tablename__ = "data_contracts"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    provider_domain = Column(String(64), nullable=False)
    consumer_domain = Column(String(64), nullable=False)
    data_product_name = Column(String(128), nullable=False)
    schema_version = Column(String(8), default="1.0")
    sla = Column(JSON, default=dict)
    terms = Column(JSON, default=dict)
    status = Column(String(16), default="draft")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(Text)
    policy_type = Column(String(32), nullable=False)
    rule = Column(JSON, nullable=False)
    effect = Column(String(16), default="deny")
    priority = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text)
    owner = Column(String(64))
    database = Column(String(64))
    schema_name = Column(String(64), default="public")
    storage_quota_gb = Column(Float, default=10.0)
    status = Column(String(16), default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    action = Column(String(64), nullable=False)
    actor = Column(String(64), nullable=False)
    resource_type = Column(String(32))
    resource_id = Column(String(64))
    details = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
