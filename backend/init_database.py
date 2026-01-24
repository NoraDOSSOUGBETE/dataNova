"""
Script d'initialisation de la base de données

Crée toutes les tables nécessaires pour DataNova Agent 1A/1B

Usage:
    python init_database.py
    # ou
    uv run python init_database.py
"""

from src.storage.database import engine
from src.storage.models import Base

def init_database():
    """Initialise la base de données en créant toutes les tables"""
    print("🔧 Initialisation de la base de données...")
    print(f"📂 Emplacement: {engine.url}")
    
    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Base de données initialisée avec succès!")
    print("\nTables créées:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    init_database()
