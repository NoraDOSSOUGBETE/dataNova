"""
SQLAlchemy Models pour Agent 1

Documentation complète: docs/DATABASE_SCHEMA.md
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, String, DateTime, Text, JSON, Boolean, Float, Integer, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid():
    """Génère un UUID v4 comme string"""
    return str(uuid4())


class Document(Base):
    """
    Documents réglementaires collectés par Agent 1A
    
    Attributes:
        id: Identifiant unique
        title: Titre du document
        source_url: URL d'origine (EUR-Lex)
        regulation_type: Type de réglementation (CBAM, EUDR, etc.)
        publication_date: Date de publication officielle
        hash_sha256: Hash SHA-256 du contenu (détection changements)
        content: Texte extrait du PDF
        nc_codes: Liste des codes NC trouvés (JSON)
        metadata: Métadonnées diverses (JSON)
        status: new, modified, unchanged
        first_seen: Date de première détection
        last_checked: Date de dernière vérification
    """
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(500), nullable=False)
    source_url = Column(String(1000), nullable=False)
    regulation_type = Column(String(50), nullable=False)
    publication_date = Column(DateTime, nullable=True)
    hash_sha256 = Column(String(64), unique=True, nullable=False)
    content = Column(Text, nullable=True)
    nc_codes = Column(JSON, nullable=True)
    document_metadata = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="new")
    first_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_checked = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relations
    analyses = relationship("Analysis", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title[:50]}, status={self.status})>"


class Analysis(Base):
    """
    Résultats d'analyse de pertinence par Agent 1B
    
    Attributes:
        id: Identifiant unique
        document_id: Référence au document analysé
        keyword_match: Niveau 1 passé (mots-clés)
        keyword_score: Score mots-clés (0-1)
        matched_keywords: Liste des mots-clés trouvés (JSON)
        nc_code_match: Niveau 2 passé (codes NC)
        nc_code_score: Score codes NC (0-1)
        matched_nc_codes: Codes NC correspondants (JSON)
        llm_score: Score sémantique LLM (0-1)
        llm_reasoning: Explication du LLM
        total_score: Score final pondéré (0-1)
        criticality: CRITICAL, HIGH, MEDIUM, LOW
        relevant: Document pertinent ou non
    """
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    
    # Niveau 1: Filtrage par mots-clés
    keyword_match = Column(Boolean, nullable=False, default=False)
    keyword_score = Column(Float, nullable=False, default=0.0)
    matched_keywords = Column(JSON, nullable=True)
    
    # Niveau 2: Filtrage par codes NC
    nc_code_match = Column(Boolean, nullable=False, default=False)
    nc_code_score = Column(Float, nullable=False, default=0.0)
    matched_nc_codes = Column(JSON, nullable=True)
    
    # Niveau 3: Analyse sémantique LLM
    llm_score = Column(Float, nullable=False, default=0.0)
    llm_reasoning = Column(Text, nullable=True)
    
    # Score final
    total_score = Column(Float, nullable=False, default=0.0)
    criticality = Column(String(20), nullable=False)
    relevant = Column(Boolean, nullable=False, default=False)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relations
    document = relationship("Document", back_populates="analyses")
    alerts = relationship("Alert", back_populates="analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, score={self.total_score:.2f}, criticality={self.criticality})>"


class Alert(Base):
    """
    Alertes générées et statut d'envoi
    
    Attributes:
        id: Identifiant unique
        analysis_id: Référence à l'analyse
        alert_type: Type (email, webhook, slack)
        alert_data: Contenu structuré de l'alerte (JSON)
        recipients: Liste des destinataires (JSON)
        sent_at: Date d'envoi (null si pas envoyé)
        status: pending, sent, failed
        error_message: Message d'erreur si échec
    """
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    alert_type = Column(String(50), nullable=False, default="email")
    alert_data = Column(JSON, nullable=False)
    recipients = Column(JSON, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relations
    analysis = relationship("Analysis", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, status={self.status})>"


class ExecutionLog(Base):
    """
    Logs d'exécution des agents (monitoring)
    
    Attributes:
        id: Identifiant unique
        agent_type: agent_1a ou agent_1b
        status: success, error, running
        start_time: Début de l'exécution
        end_time: Fin de l'exécution
        duration_seconds: Durée totale
        documents_processed: Nombre de documents traités
        documents_new: Nouveaux documents
        documents_modified: Documents modifiés
        errors: Liste des erreurs (JSON)
        metadata: Métadonnées diverses (JSON)
    """
    __tablename__ = "execution_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="running")
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    documents_processed = Column(Integer, default=0)
    documents_new = Column(Integer, default=0)
    documents_modified = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)
    log_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ExecutionLog(id={self.id}, agent={self.agent_type}, status={self.status})>"


class CompanyProfile(Base):
    """
    Profils entreprise pour filtrage personnalisé (Agent 1B)
    
    Attributes:
        id: Identifiant unique
        company_name: Nom de l'entreprise
        nc_codes: Codes NC pertinents (JSON)
        keywords: Mots-clés à surveiller (JSON)
        regulations: Réglementations à surveiller (JSON)
        contact_emails: Emails pour alertes (JSON)
        config: Configuration personnalisée (JSON)
        active: Profil actif ou non
    """
    __tablename__ = "company_profiles"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    company_name = Column(String(200), nullable=False)
    nc_codes = Column(JSON, nullable=False)
    keywords = Column(JSON, nullable=False)
    regulations = Column(JSON, nullable=False)
    contact_emails = Column(JSON, nullable=False)
    config = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CompanyProfile(id={self.id}, name={self.company_name}, active={self.active})>"
