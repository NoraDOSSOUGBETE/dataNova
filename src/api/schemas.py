"""Modèles Pydantic pour l'API."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================
# Documents
# ============================================================

class DocumentBase(BaseModel):
    """Schéma de base pour un document."""
    title: str
    source_url: str
    content: str
    nc_codes: List[str] = []
    regulation_type: str = "CBAM"
    publication_date: Optional[datetime] = None
    document_metadata: Optional[Dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    """Schéma pour créer un document."""
    hash_sha256: str


class DocumentUpdate(BaseModel):
    """Schéma pour mettre à jour un document."""
    title: Optional[str] = None
    content: Optional[str] = None
    nc_codes: Optional[List[str]] = None
    status: Optional[str] = None
    workflow_status: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Schéma de réponse pour un document."""
    id: str
    hash_sha256: str
    status: str
    workflow_status: str
    created_at: datetime
    updated_at: datetime
    last_checked: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# Profils Entreprise
# ============================================================

class CompanyProfileBase(BaseModel):
    """Schéma de base pour un profil entreprise."""
    name: str
    industry_sector: str
    nc_codes: List[str] = []
    countries: List[str] = []
    annual_imports_tons: Optional[float] = None
    profile_metadata: Optional[Dict[str, Any]] = None


class CompanyProfileCreate(CompanyProfileBase):
    """Schéma pour créer un profil entreprise."""
    pass


class CompanyProfileUpdate(BaseModel):
    """Schéma pour mettre à jour un profil entreprise."""
    name: Optional[str] = None
    industry_sector: Optional[str] = None
    nc_codes: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    annual_imports_tons: Optional[float] = None
    profile_metadata: Optional[Dict[str, Any]] = None


class CompanyProfileResponse(CompanyProfileBase):
    """Schéma de réponse pour un profil entreprise."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# Analyses
# ============================================================

class AnalysisBase(BaseModel):
    """Schéma de base pour une analyse."""
    document_id: str
    is_relevant: bool = False
    confidence: float = 0.0
    matched_keywords: List[str] = []
    matched_nc_codes: List[str] = []
    llm_reasoning: Optional[str] = None
    validation_comment: Optional[str] = None


class AnalysisCreate(AnalysisBase):
    """Schéma pour créer une analyse."""
    pass


class AnalysisResponse(AnalysisBase):
    """Schéma de réponse pour une analyse."""
    id: str
    validation_status: str
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# Alertes
# ============================================================

class AlertBase(BaseModel):
    """Schéma de base pour une alerte."""
    impact_id: str
    alert_type: str
    message: str
    priority: str = "medium"


class AlertCreate(AlertBase):
    """Schéma pour créer une alerte."""
    pass


class AlertResponse(AlertBase):
    """Schéma de réponse pour une alerte."""
    id: str
    sent_at: Optional[datetime] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# Réponses paginées
# ============================================================

class PaginatedResponse(BaseModel):
    """Schéma pour les réponses paginées."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
