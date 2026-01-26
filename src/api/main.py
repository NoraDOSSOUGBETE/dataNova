"""Application FastAPI principale."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import documents, profiles, analyses, alerts, regulations
from src.config import settings

app = FastAPI(
    title="DataNova API",
    description="API REST pour la gestion de la veille réglementaire",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Vite dev server (port alternatif)
        "http://localhost:5173",  # Vite dev server
        "http://localhost:4200",  # Angular dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["Profils"])
app.include_router(analyses.router, prefix="/api/analyses", tags=["Analyses"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alertes"])
app.include_router(regulations.router, prefix="/api/regulations", tags=["Réglementations"])


@app.get("/")
async def root():
    """Route racine."""
    return {
        "message": "Bienvenue sur l'API DataNova",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API."""
    return {"status": "healthy"}
