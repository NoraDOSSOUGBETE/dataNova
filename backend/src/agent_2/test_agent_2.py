# test_agent_2_with_real_data.py
from dotenv import load_dotenv
load_dotenv()  # Charge automatiquement le fichier .env
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path
import json


# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent))
from storage.models import HutchinsonSite, Supplier, SupplierRelationship, Document, PertinenceCheck
from agent_2.agent import Agent2


# Connexion à la base (chemin absolu pour éviter les problèmes)
db_path = Path(__file__).parent.parent.parent / "ping_test.db"
engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)
session = Session()


# Charger les données réelles
sites = session.query(HutchinsonSite).all()
suppliers = session.query(Supplier).all()
relationships = session.query(SupplierRelationship).all()
documents = session.query(Document).all()


# Convertir les objets SQLAlchemy en dictionnaires (une seule fois)
sites_dict = [
    {
        "id": s.id,
        "name": s.name,
        "country": s.country,
        "region": s.region,
        "city": s.city,
        "latitude": s.latitude,
        "longitude": s.longitude,
        "sectors": s.sectors or [],
        "main_products": s.products or [],
        "products": s.products or [],
        "raw_materials": s.raw_materials or [],
        "employee_count": s.employee_count or 0,
        "annual_production_value": s.annual_production_value or 0,
        "strategic_importance": s.strategic_importance or "moyen",
        "certifications": s.certifications or [],
        "sectors_served": s.sectors or []
    }
    for s in sites
]

suppliers_dict = [
    {
        "id": sup.id,
        "name": sup.name,
        "code": sup.code,
        "country": sup.country,
        "region": sup.region,
        "city": sup.city,
        "latitude": sup.latitude,
        "longitude": sup.longitude,
        "products_supplied": sup.products_supplied or [],
        "sector": sup.sector or "Inconnu",
        "company_size": sup.company_size or "PME",
        "financial_health": sup.financial_health or "moyen",
        "certifications": sup.certifications or []
    }
    for sup in suppliers
]

relationships_dict = [
    {
        "site_id": r.hutchinson_site_id,
        "supplier_id": r.supplier_id,
        "products_supplied": r.products_supplied or [],
        "criticality": r.criticality or "Standard",
        "is_sole_supplier": r.is_sole_supplier or False,
        "is_unique_supplier": r.is_sole_supplier or False,
        "has_backup_supplier": r.has_backup_supplier or False,
        "backup_supplier_id": r.backup_supplier_id,
        "lead_time_days": r.lead_time_days or 30,
        "annual_volume_eur": r.annual_volume or 0
    }
    for r in relationships
]


# Initialiser Agent 2
agent2 = Agent2(llm_model="claude-sonnet-4-20250514")


# ============================================================================
# TESTER LES 3 SCÉNARIOS
# ============================================================================

print("=" * 80)
print("🧪 TESTS AGENT 2 - 3 SCÉNARIOS")
print("=" * 80)

for i, doc in enumerate(documents, 1):
    print(f"\n{'=' * 80}")
    print(f"🧪 TEST {i}: {doc.title} ({doc.event_type})")
    print("=" * 80)
    
    # Simuler le résultat de pertinence (Agent 1B)
    pertinence_mock = {
        "decision": "OUI",
        "confidence": 0.95,
        "reasoning": f"Événement {doc.event_type} majeur affectant Hutchinson",
        "affected_entities_preview": {
            "sites": [],  # Agent 2 va les identifier
            "suppliers": []
        }
    }
    
    doc_dict = {
        "id": doc.id,
        "title": doc.title,
        "event_type": doc.event_type,
        "geographic_scope": doc.geographic_scope,
        "content": doc.content
    }
    
    # Analyser
    print(f"\n🚀 Analyse en cours pour {doc.event_type}...")
    try:
        result = agent2.analyze(
            document=doc_dict,
            pertinence_result=pertinence_mock,
            sites=sites_dict,
            suppliers=suppliers_dict,
            supplier_relationships=relationships_dict
        )
        
        print(f"\n✅ Résultat de l'analyse ({doc.event_type}):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Résumé compact
        print(f"\n📊 RÉSUMÉ {doc.event_type.upper()}:")
        print(f"  - Sites impactés: {result['affected_sites_count']}")
        print(f"  - Fournisseurs impactés: {result['affected_suppliers_count']}")
        print(f"  - Niveau de risque: {result['overall_risk_level']}")
        print(f"  - Méthode de projection: {result['projection_method']}")
        print(f"  - Nombre de recommandations: {len(result.get('recommendations', []))}")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'analyse {doc.event_type}: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 80}")
print("✅ TESTS TERMINÉS")
print("=" * 80)
