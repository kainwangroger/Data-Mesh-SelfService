"""
Governance API — Metadata Registry + Policy Engine.

FastAPI service exposant :
- CRUD Data Products / Data Contracts / Policies / Domains
- Policy evaluation endpoint
"""

import os
from pathlib import Path
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models import Base, DataProduct, DataContract, Policy, Domain, AuditLog
from schemas import (
    DataProductCreate, DataProductResponse,
    DataContractCreate, DataContractResponse,
    PolicyCreate, PolicyResponse,
    DomainCreate, DomainResponse,
)
from policy import PolicyEngine, DEFAULT_POLICIES


# ── Database setup ──────────────────────────

GOVERNANCE_DB = os.getenv("GOVERNANCE_DB", "sqlite:///data/governance.db")
engine = create_engine(GOVERNANCE_DB, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    db_path = GOVERNANCE_DB.replace("sqlite:///", "").replace("sqlite://", "")
    if db_path:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if db.query(Policy).count() == 0:
            for p in DEFAULT_POLICIES:
                db.add(Policy(**p))
            db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── FastAPI app ──────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Data Mesh Governance API", version="1.0.0", lifespan=lifespan)


# ── Data Products ────────────────────────────

@app.post("/data-products", response_model=DataProductResponse)
def create_data_product(dp: DataProductCreate, db: Session = Depends(get_db)):
    existing = db.query(DataProduct).filter(DataProduct.name == dp.name).first()
    if existing:
        raise HTTPException(409, f"Data product '{dp.name}' already exists")
    obj = DataProduct(**dp.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _log_audit(db, "create", "admin", "data_product", obj.name)
    return obj


@app.get("/data-products", response_model=list[DataProductResponse])
def list_data_products(domain: str = None, db: Session = Depends(get_db)):
    q = db.query(DataProduct)
    if domain:
        q = q.filter(DataProduct.domain == domain)
    return q.all()


@app.get("/data-products/{dp_id}", response_model=DataProductResponse)
def get_data_product(dp_id: int, db: Session = Depends(get_db)):
    dp = db.query(DataProduct).filter(DataProduct.id == dp_id).first()
    if not dp:
        raise HTTPException(404)
    return dp


# ── Data Contracts ───────────────────────────

@app.post("/data-contracts", response_model=DataContractResponse)
def create_data_contract(dc: DataContractCreate, db: Session = Depends(get_db)):
    obj = DataContract(**dc.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _log_audit(db, "create", "admin", "data_contract", obj.name)
    return obj


@app.get("/data-contracts", response_model=list[DataContractResponse])
def list_data_contracts(db: Session = Depends(get_db)):
    return db.query(DataContract).all()


@app.get("/data-contracts/{dc_id}", response_model=DataContractResponse)
def get_data_contract(dc_id: int, db: Session = Depends(get_db)):
    dc = db.query(DataContract).filter(DataContract.id == dc_id).first()
    if not dc:
        raise HTTPException(404)
    return dc


# ── Policies ─────────────────────────────────

@app.post("/policies", response_model=PolicyResponse)
def create_policy(p: PolicyCreate, db: Session = Depends(get_db)):
    obj = Policy(**p.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/policies", response_model=list[PolicyResponse])
def list_policies(enabled: bool = None, db: Session = Depends(get_db)):
    q = db.query(Policy)
    if enabled is not None:
        q = q.filter(Policy.enabled == enabled)
    return q.all()


# ── Policy Evaluation ────────────────────────

@app.post("/evaluate")
def evaluate_access(
    actor: str,
    action: str,
    resource: dict,
    db: Session = Depends(get_db),
):
    policies = db.query(Policy).all()
    policy_dicts = [
        {
            "name": p.name,
            "policy_type": p.policy_type,
            "priority": p.priority,
            "effect": p.effect,
            "enabled": p.enabled,
            "rule": p.rule,
        }
        for p in policies
    ]
    engine = PolicyEngine()
    result = engine.evaluate(actor, action, resource, policy_dicts)
    _log_audit(db, "evaluate", actor, "access", f"{action} on {resource.get('name','?')}", result)
    return result


# ── Domains ──────────────────────────────────

@app.post("/domains", response_model=DomainResponse)
def create_domain(d: DomainCreate, db: Session = Depends(get_db)):
    obj = Domain(**d.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _log_audit(db, "create", d.owner or "admin", "domain", obj.name)
    return obj


@app.get("/domains", response_model=list[DomainResponse])
def list_domains(db: Session = Depends(get_db)):
    return db.query(Domain).all()


# ── Audit log ────────────────────────────────

@app.get("/audit-logs")
def list_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )


# ── Health ───────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "governance-api", "version": "1.0.0"}


# ── Helpers ──────────────────────────────────

def _log_audit(db, action, actor, resource_type, resource_id, details=None):
    log = AuditLog(
        action=action,
        actor=actor,
        resource_type=resource_type,
        resource_id=str(resource_id)[:64],
        details=details,
    )
    db.add(log)
    db.commit()
