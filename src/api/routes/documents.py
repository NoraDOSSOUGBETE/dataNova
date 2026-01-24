"""Routes pour les documents."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.schemas import DocumentCreate, DocumentResponse, DocumentUpdate, PaginatedResponse
from src.storage.database import get_db
from src.storage.repositories import DocumentRepository

router = APIRouter()


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    regulation_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lister les documents avec filtres optionnels."""
    repo = DocumentRepository(db)
    
    query = db.query(repo.model)
    
    if status:
        query = query.filter(repo.model.status == status)
    if regulation_type:
        query = query.filter(repo.model.regulation_type == regulation_type)
    
    documents = query.offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Récupérer un document par son ID."""
    repo = DocumentRepository(db)
    document = repo.find_by_id(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    return document


@router.post("/", response_model=DocumentResponse, status_code=201)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """Créer un nouveau document (ou mettre à jour si existant)."""
    repo = DocumentRepository(db)
    
    doc, status = repo.upsert_document(
        source_url=document.source_url,
        hash_sha256=document.hash_sha256,
        title=document.title,
        content=document.content,
        nc_codes=document.nc_codes,
        regulation_type=document.regulation_type,
        publication_date=document.publication_date,
        document_metadata=document.document_metadata
    )
    
    db.commit()
    return doc


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour un document existant."""
    repo = DocumentRepository(db)
    document = repo.find_by_id(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    # Mettre à jour les champs fournis
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Supprimer un document."""
    repo = DocumentRepository(db)
    document = repo.find_by_id(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    db.delete(document)
    db.commit()
    return None


@router.get("/search/by-nc-code", response_model=List[DocumentResponse])
def search_documents_by_nc_code(
    nc_code: str = Query(..., description="Code NC à rechercher"),
    db: Session = Depends(get_db)
):
    """Rechercher des documents par code NC."""
    repo = DocumentRepository(db)
    documents = repo.find_by_nc_codes([nc_code])
    return documents
