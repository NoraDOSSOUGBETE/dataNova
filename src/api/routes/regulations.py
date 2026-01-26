"""Routes pour les réglementations (wrapper autour des analyses)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from src.storage.database import get_db
from src.storage.models import Analysis, Document

router = APIRouter()


# Schémas pour les réglementations
class RegulationResponse(BaseModel):
    """Schéma de réponse pour une réglementation."""
    id: str
    title: str
    description: str
    status: str  # pending, validated, rejected, to-review
    type: str
    dateCreated: datetime
    reference: Optional[str] = None

    class Config:
        from_attributes = True


class RegulationListResponse(BaseModel):
    """Schéma de réponse pour la liste des réglementations."""
    regulations: List[RegulationResponse]
    total: int
    page: int
    limit: int


class UpdateRegulationRequest(BaseModel):
    """Schéma pour mettre à jour le statut d'une réglementation."""
    status: str  # validated, rejected, to-review
    comment: Optional[str] = None


def map_validation_status_to_frontend(backend_status: str) -> str:
    """Mapper le statut backend vers le statut frontend."""
    mapping = {
        "pending": "to-review",
        "approved": "validated",
        "rejected": "rejected"
    }
    return mapping.get(backend_status, "to-review")


def map_frontend_status_to_backend(frontend_status: str) -> str:
    """Mapper le statut frontend vers le statut backend."""
    mapping = {
        "to-review": "pending",
        "validated": "approved",
        "rejected": "rejected"
    }
    return mapping.get(frontend_status, "pending")


@router.get("/", response_model=RegulationListResponse)
def get_regulations(
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    search: Optional[str] = Query(None, description="Recherche dans le titre"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Récupérer toutes les réglementations avec filtres.
    
    Les réglementations sont créées à partir des analyses et de leurs documents associés.
    """
    # Construire la requête avec jointure
    query = db.query(Analysis).join(Document, Analysis.document_id == Document.id)
    
    # Filtrer par statut si fourni
    if status and status != "all":
        backend_status = map_frontend_status_to_backend(status)
        query = query.filter(Analysis.validation_status == backend_status)
    
    # Recherche dans le titre du document
    if search:
        query = query.filter(Document.title.ilike(f"%{search}%"))
    
    # Pagination
    total = query.count()
    skip = (page - 1) * limit
    analyses = query.offset(skip).limit(limit).all()
    
    # Mapper vers le format frontend
    regulations = []
    for analysis in analyses:
        document = db.query(Document).filter(Document.id == analysis.document_id).first()
        
        if document:
            # Créer une description à partir du contenu du document
            description = document.content[:200] + "..." if document.content and len(document.content) > 200 else (document.content or "")
            
            regulation = RegulationResponse(
                id=analysis.id,
                title=document.title,
                description=description,
                status=map_validation_status_to_frontend(analysis.validation_status),
                type=document.regulation_type,
                dateCreated=analysis.created_at,
                reference=document.source_url
            )
            regulations.append(regulation)
    
    return RegulationListResponse(
        regulations=regulations,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{regulation_id}", response_model=RegulationResponse)
def get_regulation(regulation_id: str, db: Session = Depends(get_db)):
    """
    Récupérer une réglementation par son ID.
    
    L'ID correspond à l'ID de l'analyse.
    """
    analysis = db.query(Analysis).filter(Analysis.id == regulation_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Réglementation non trouvée")
    
    document = db.query(Document).filter(Document.id == analysis.document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document associé non trouvé")
    
    description = document.content[:200] + "..." if document.content and len(document.content) > 200 else (document.content or "")
    
    return RegulationResponse(
        id=analysis.id,
        title=document.title,
        description=description,
        status=map_validation_status_to_frontend(analysis.validation_status),
        type=document.regulation_type,
        dateCreated=analysis.created_at,
        reference=document.source_url
    )


@router.get("/stats")
def get_regulations_stats(db: Session = Depends(get_db)):
    """
    Récupérer les statistiques des réglementations.
    
    Endpoint requis par le frontend pour afficher les métriques du dashboard.
    """
    # Compter le total
    total = db.query(Analysis).count()
    
    # Compter par statut (backend)
    pending_count = db.query(Analysis).filter(Analysis.validation_status == "pending").count()
    validated_count = db.query(Analysis).filter(Analysis.validation_status == "approved").count()
    rejected_count = db.query(Analysis).filter(Analysis.validation_status == "rejected").count()
    
    # Calculer les réglementations récentes (derniers 7 jours)
    from datetime import timedelta
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_count = db.query(Analysis).filter(Analysis.created_at >= seven_days_ago).count()
    
    # Compter les priorités hautes (à adapter selon vos critères)
    # Pour l'instant, on considère les analyses pending comme prioritaires
    high_priority = pending_count
    
    return {
        "total": total,
        "by_status": {
            "pending": pending_count,
            "validated": validated_count,
            "rejected": rejected_count
        },
        "recent_count": recent_count,
        "high_priority": high_priority
    }


@router.put("/{regulation_id}/status", response_model=RegulationResponse)
def update_regulation_status(
    regulation_id: str,
    data: UpdateRegulationRequest,
    db: Session = Depends(get_db)
):
    """
    Mettre à jour le statut d'une réglementation.
    
    Cette route est utilisée par l'équipe juridique pour valider/rejeter les réglementations.
    """
    analysis = db.query(Analysis).filter(Analysis.id == regulation_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Réglementation non trouvée")
    
    # Mapper le statut frontend vers backend
    backend_status = map_frontend_status_to_backend(data.status)
    
    # Mettre à jour l'analyse
    analysis.validation_status = backend_status
    
    if data.comment:
        analysis.validation_comment = data.comment
    
    analysis.validated_at = datetime.now()
    
    db.commit()
    db.refresh(analysis)
    
    # Récupérer le document pour la réponse
    document = db.query(Document).filter(Document.id == analysis.document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document associé non trouvé")
    
    description = document.content[:200] + "..." if document.content and len(document.content) > 200 else (document.content or "")
    
    return RegulationResponse(
        id=analysis.id,
        title=document.title,
        description=description,
        status=map_validation_status_to_frontend(analysis.validation_status),
        type=document.regulation_type,
        dateCreated=analysis.created_at,
        reference=document.source_url
    )
