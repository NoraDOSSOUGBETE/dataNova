"""Routes pour les profils entreprise."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.schemas import CompanyProfileCreate, CompanyProfileResponse, CompanyProfileUpdate
from src.storage.database import get_db
from src.storage.repositories import CompanyProfileRepository

router = APIRouter()


@router.get("/", response_model=List[CompanyProfileResponse])
def list_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Lister tous les profils entreprise."""
    repo = CompanyProfileRepository(db)
    profiles = db.query(repo.model).offset(skip).limit(limit).all()
    return profiles


@router.get("/{profile_id}", response_model=CompanyProfileResponse)
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """Récupérer un profil entreprise par son ID."""
    repo = CompanyProfileRepository(db)
    profile = repo.find_by_id(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    return profile


@router.post("/", response_model=CompanyProfileResponse, status_code=201)
def create_profile(profile: CompanyProfileCreate, db: Session = Depends(get_db)):
    """Créer un nouveau profil entreprise."""
    repo = CompanyProfileRepository(db)
    
    db_profile = repo.model(
        name=profile.name,
        industry_sector=profile.industry_sector,
        nc_codes=profile.nc_codes,
        countries=profile.countries,
        annual_imports_tons=profile.annual_imports_tons,
        profile_metadata=profile.profile_metadata or {}
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.put("/{profile_id}", response_model=CompanyProfileResponse)
def update_profile(
    profile_id: str,
    profile_update: CompanyProfileUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un profil entreprise."""
    repo = CompanyProfileRepository(db)
    profile = repo.find_by_id(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{profile_id}", status_code=204)
def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    """Supprimer un profil entreprise."""
    repo = CompanyProfileRepository(db)
    profile = repo.find_by_id(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    
    db.delete(profile)
    db.commit()
    return None
