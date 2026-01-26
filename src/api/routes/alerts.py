"""Routes pour les alertes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.schemas import AlertCreate, AlertResponse
from src.storage.database import get_db
from src.storage.repositories import AlertRepository

router = APIRouter()


@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lister les alertes avec filtres optionnels."""
    repo = AlertRepository(db)
    
    query = db.query(repo.model)
    
    if status:
        query = query.filter(repo.model.status == status)
    if priority:
        query = query.filter(repo.model.priority == priority)
    
    alerts = query.offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """Récupérer une alerte par son ID."""
    repo = AlertRepository(db)
    alert = repo.find_by_id(alert_id)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    return alert


@router.post("/", response_model=AlertResponse, status_code=201)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle alerte."""
    repo = AlertRepository(db)
    
    db_alert = repo.model(
        impact_id=alert.impact_id,
        alert_type=alert.alert_type,
        message=alert.message,
        priority=alert.priority,
        status="pending"
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.delete("/{alert_id}", status_code=204)
def delete_alert(alert_id: str, db: Session = Depends(get_db)):
    """Supprimer une alerte."""
    repo = AlertRepository(db)
    alert = repo.find_by_id(alert_id)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    db.delete(alert)
    db.commit()
    return None
