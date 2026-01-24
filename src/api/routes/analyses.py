"""Routes pour les analyses."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.schemas import AnalysisCreate, AnalysisResponse
from src.storage.database import get_db
from src.storage.repositories import AnalysisRepository
from src.storage.models import Analysis

router = APIRouter()


@router.get("/", response_model=List[AnalysisResponse])
def list_analyses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    document_id: Optional[str] = None,
    validation_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lister les analyses avec filtres optionnels."""
    query = db.query(Analysis)
    
    if document_id:
        query = query.filter(Analysis.document_id == document_id)
    if validation_status:
        query = query.filter(Analysis.validation_status == validation_status)
    
    analyses = query.offset(skip).limit(limit).all()
    return analyses


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Récupérer une analyse par son ID."""
    repo = AnalysisRepository(db)
    analysis = repo.find_by_id(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    
    return analysis


@router.post("/", response_model=AnalysisResponse, status_code=201)
def create_analysis(analysis: AnalysisCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle analyse."""
    repo = AnalysisRepository(db)
    
    db_analysis = repo.model(
        document_id=analysis.document_id,
        is_relevant=analysis.is_relevant,
        confidence=analysis.confidence,
        matched_keywords=analysis.matched_keywords,
        matched_nc_codes=analysis.matched_nc_codes,
        llm_reasoning=analysis.llm_reasoning,
        validation_status="pending"
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


@router.put("/{analysis_id}/validate", response_model=AnalysisResponse)
def validate_analysis(
    analysis_id: str,
    status: str = Query(..., pattern="^(approved|rejected)$", description="approved ou rejected"),
    db: Session = Depends(get_db)
):
    """
    Valider ou rejeter une analyse (pour l'équipe juridique).
    
    Args:
        analysis_id: ID de l'analyse
        status: "approved" pour approuver, "rejected" pour rejeter
    
    Returns:
        L'analyse mise à jour
    """
    repo = AnalysisRepository(db)
    analysis = repo.find_by_id(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    
    # Mettre à jour le statut de validation
    analysis.validation_status = status
    
    db.commit()
    db.refresh(analysis)
    
    return analysis


@router.delete("/{analysis_id}", status_code=204)
def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Supprimer une analyse."""
    repo = AnalysisRepository(db)
    analysis = repo.find_by_id(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    
    db.delete(analysis)
    db.commit()
    return None
