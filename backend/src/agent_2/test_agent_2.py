"""
Script de Test pour Agent 2

Ce script teste Agent 2 avec des données fictives pour les 3 types d'événements :
- Climatique (inondation en Thaïlande)
- Réglementaire (CBAM en Europe)
- Géopolitique (conflit en Ukraine)
"""

import json
from agent import Agent2


# ============================================================================
# DONNÉES MOCK
# ============================================================================

# Sites Hutchinson fictifs
MOCK_SITES = [
    {
        "id": "site1",
        "name": "Bangkok Manufacturing Plant",
        "country": "Thailand",
        "region": "Bangkok",
        "latitude": 13.7563,
        "longitude": 100.5018,
        "sectors": ["automotive", "aerospace"],
        "main_products": ["rubber seals", "gaskets", "vibration control"],
        "raw_materials": ["natural rubber", "synthetic rubber"],
        "certifications": ["ISO 9001", "IATF 16949"],
        "employee_count": 850,
        "annual_production_value": 28_000_000,
        "strategic_importance": "critique"
    },
    {
        "id": "site2",
        "name": "Rayong Production Facility",
        "country": "Thailand",
        "region": "Rayong",
        "latitude": 12.6814,
        "longitude": 101.2815,
        "sectors": ["automotive"],
        "main_products": ["rubber seals", "hoses"],
        "raw_materials": ["natural rubber"],
        "certifications": ["ISO 9001"],
        "employee_count": 450,
        "annual_production_value": 15_000_000,
        "strategic_importance": "fort"
    },
    {
        "id": "site3",
        "name": "Paris R&D Center",
        "country": "France",
        "region": "Île-de-France",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "sectors": ["automotive", "aerospace", "industrial"],
        "main_products": ["prototypes", "advanced materials"],
        "raw_materials": ["specialty polymers"],
        "certifications": ["ISO 9001", "ISO 14001"],
        "employee_count": 320,
        "annual_production_value": 5_000_000,
        "strategic_importance": "critique"
    },
    {
        "id": "site4",
        "name": "Warsaw Manufacturing Plant",
        "country": "Poland",
        "region": "Mazovia",
        "latitude": 52.2297,
        "longitude": 21.0122,
        "sectors": ["automotive"],
        "main_products": ["rubber components", "seals"],
        "raw_materials": ["synthetic rubber"],
        "certifications": ["ISO 9001"],
        "employee_count": 600,
        "annual_production_value": 18_000_000,
        "strategic_importance": "fort"
    }
]

# Fournisseurs fictifs
MOCK_SUPPLIERS = [
    {
        "id": "sup1",
        "name": "Thai Rubber Industries Co.",
        "country": "Thailand",
        "region": "Bangkok",
        "latitude": 13.8000,
        "longitude": 100.5500,
        "sector": "raw materials",
        "products_supplied": ["natural rubber", "latex"],
        "company_size": "ETI",
        "certifications": ["ISO 9001"],
        "financial_health": "bon"
    },
    {
        "id": "sup2",
        "name": "Bangkok Chemical Supplies",
        "country": "Thailand",
        "region": "Bangkok",
        "latitude": 13.7000,
        "longitude": 100.4500,
        "sector": "chemicals",
        "products_supplied": ["additives", "catalysts"],
        "company_size": "PME",
        "certifications": [],
        "financial_health": "moyen"
    },
    {
        "id": "sup3",
        "name": "European Polymers GmbH",
        "country": "Germany",
        "region": "Bavaria",
        "latitude": 48.1351,
        "longitude": 11.5820,
        "sector": "raw materials",
        "products_supplied": ["synthetic rubber", "specialty polymers"],
        "company_size": "Grand groupe",
        "certifications": ["ISO 9001", "ISO 14001"],
        "financial_health": "excellent"
    },
    {
        "id": "sup4",
        "name": "Polish Components Sp. z o.o.",
        "country": "Poland",
        "region": "Mazovia",
        "latitude": 52.1000,
        "longitude": 21.0000,
        "sector": "components",
        "products_supplied": ["metal parts", "fasteners"],
        "company_size": "PME",
        "certifications": ["ISO 9001"],
        "financial_health": "bon"
    },
    {
        "id": "sup5",
        "name": "Ukrainian Steel Works",
        "country": "Ukraine",
        "region": "Kyiv",
        "latitude": 50.4501,
        "longitude": 30.5234,
        "sector": "raw materials",
        "products_supplied": ["steel", "metal alloys"],
        "company_size": "Grand groupe",
        "certifications": ["ISO 9001"],
        "financial_health": "faible"
    }
]

# Relations fournisseur-site (enrichies avec stocks et délais)
MOCK_RELATIONSHIPS = [
    {
        "id": "rel1",
        "site_id": "site1",
        "supplier_id": "sup1",
        "site_name": "Bangkok Manufacturing Plant",
        "supplier_name": "Thai Rubber Industries Co.",
        "criticality": "Critique",
        "is_unique_supplier": True,
        "backup_supplier_id": None,
        "annual_volume_eur": 8_000_000,
        "lead_time_days": 15,
        "stock_safety_days": 14,  # Stock de sécurité de 2 semaines
        "products_supplied": ["natural rubber", "latex"]
    },
    {
        "id": "rel2",
        "site_id": "site1",
        "supplier_id": "sup2",
        "site_name": "Bangkok Manufacturing Plant",
        "supplier_name": "Bangkok Chemical Supplies",
        "criticality": "Important",
        "is_unique_supplier": False,
        "backup_supplier_id": "sup3",
        "annual_volume_eur": 2_000_000,
        "lead_time_days": 20,
        "stock_safety_days": 21,
        "products_supplied": ["additives", "catalysts"]
    },
    {
        "id": "rel3",
        "site_id": "site2",
        "supplier_id": "sup1",
        "site_name": "Rayong Production Facility",
        "supplier_name": "Thai Rubber Industries Co.",
        "criticality": "Critique",
        "is_unique_supplier": True,
        "backup_supplier_id": None,
        "annual_volume_eur": 5_000_000,
        "lead_time_days": 15,
        "stock_safety_days": 10,
        "products_supplied": ["natural rubber"]
    },
    {
        "id": "rel4",
        "site_id": "site3",
        "supplier_id": "sup3",
        "site_name": "Paris R&D Center",
        "supplier_name": "European Polymers GmbH",
        "criticality": "Important",
        "is_unique_supplier": False,
        "backup_supplier_id": None,
        "annual_volume_eur": 1_500_000,
        "lead_time_days": 10,
        "stock_safety_days": 30,
        "products_supplied": ["specialty polymers"]
    },
    {
        "id": "rel5",
        "site_id": "site4",
        "supplier_id": "sup3",
        "site_name": "Warsaw Manufacturing Plant",
        "supplier_name": "European Polymers GmbH",
        "criticality": "Important",
        "is_unique_supplier": False,
        "backup_supplier_id": None,
        "annual_volume_eur": 3_000_000,
        "lead_time_days": 12,
        "stock_safety_days": 21,
        "products_supplied": ["synthetic rubber"]
    },
    {
        "id": "rel6",
        "site_id": "site4",
        "supplier_id": "sup4",
        "site_name": "Warsaw Manufacturing Plant",
        "supplier_name": "Polish Components Sp. z o.o.",
        "criticality": "Standard",
        "is_unique_supplier": False,
        "backup_supplier_id": None,
        "annual_volume_eur": 800_000,
        "lead_time_days": 7,
        "stock_safety_days": 14,
        "products_supplied": ["metal parts", "fasteners"]
    },
    {
        "id": "rel7",
        "site_id": "site4",
        "supplier_id": "sup5",
        "site_name": "Warsaw Manufacturing Plant",
        "supplier_name": "Ukrainian Steel Works",
        "criticality": "Important",
        "is_unique_supplier": False,
        "backup_supplier_id": "sup3",
        "annual_volume_eur": 2_500_000,
        "lead_time_days": 25,
        "stock_safety_days": 7,  # Stock faible à cause de la situation
        "products_supplied": ["steel", "metal alloys"]
    }
]

# Documents fictifs
MOCK_DOCUMENTS = {
    "climatique": {
        "id": "doc1",
        "title": "Severe Flooding Alert - Bangkok Metropolitan Area",
        "source_url": "https://example.com/weather/bangkok-flood-2026",
        "event_type": "climatique",
        "event_subtype": "inondation",
        "publication_date": "2026-01-28T10:00:00Z",
        "collection_date": "2026-01-28T10:15:00Z",
        "hash_sha256": "abc123...",
        "content": "Heavy rainfall expected in Bangkok area with flooding risk...",
        "summary": "Severe flooding expected in Bangkok with 200mm+ rainfall in 48h",
        "geographic_scope": {
            "countries": ["Thailand"],
            "regions": ["Bangkok", "Samut Prakan"],
            "coordinates": {
                "latitude": 13.7563,
                "longitude": 100.5018
            }
        },
        "extra_metadata": {"severity": "high", "duration_hours": 48}
    },
    "reglementaire": {
        "id": "doc2",
        "title": "EU Carbon Border Adjustment Mechanism (CBAM) - Implementation Phase 2",
        "source_url": "https://eur-lex.europa.eu/cbam-2026",
        "event_type": "reglementaire",
        "event_subtype": "CBAM",
        "publication_date": "2026-01-15T00:00:00Z",
        "collection_date": "2026-01-15T08:00:00Z",
        "hash_sha256": "def456...",
        "content": "New CBAM requirements for automotive and industrial sectors...",
        "summary": "CBAM Phase 2 extends to automotive sector, requires carbon reporting",
        "geographic_scope": {
            "countries": ["France", "Germany", "Poland", "Italy", "Spain"],
            "regions": ["European Union"],
            "coordinates": None
        },
        "extra_metadata": {"effective_date": "2026-07-01", "sectors": ["automotive", "industrial"]}
    },
    "geopolitique": {
        "id": "doc3",
        "title": "Ongoing Conflict in Ukraine - Supply Chain Disruptions",
        "source_url": "https://example.com/news/ukraine-conflict-2026",
        "event_type": "geopolitique",
        "event_subtype": "conflit",
        "publication_date": "2026-01-20T00:00:00Z",
        "collection_date": "2026-01-20T06:00:00Z",
        "hash_sha256": "ghi789...",
        "content": "Continued conflict affecting industrial production and logistics...",
        "summary": "Conflict in Ukraine continues to disrupt supply chains in Eastern Europe",
        "geographic_scope": {
            "countries": ["Ukraine"],
            "regions": ["Poland", "Romania", "Slovakia", "Hungary"],
            "coordinates": None
        },
        "extra_metadata": {"risk_level": "high", "affected_industries": ["steel", "logistics"]}
    }
}

# Résultats de pertinence fictifs
MOCK_PERTINENCE_RESULTS = {
    "climatique": {
        "decision": "OUI",
        "reasoning": "Flooding in Bangkok directly impacts our manufacturing plants",
        "confidence": 0.95
    },
    "reglementaire": {
        "decision": "OUI",
        "reasoning": "CBAM affects our automotive operations in EU",
        "confidence": 0.90
    },
    "geopolitique": {
        "decision": "PARTIELLEMENT",
        "reasoning": "Affects suppliers in Ukraine and neighboring countries",
        "confidence": 0.75
    }
}


# ============================================================================
# FONCTIONS DE TEST
# ============================================================================

def print_separator(title):
    """Affiche un séparateur visuel"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_climatique():
    """Test avec événement climatique (inondation Bangkok)"""
    print_separator("TEST 1: ÉVÉNEMENT CLIMATIQUE - Inondation Bangkok")
    
    agent = Agent2()
    
    result = agent.analyze(
        document=MOCK_DOCUMENTS["climatique"],
        pertinence_result=MOCK_PERTINENCE_RESULTS["climatique"],
        sites=MOCK_SITES,
        suppliers=MOCK_SUPPLIERS,
        supplier_relationships=MOCK_RELATIONSHIPS
    )
    
    print(f"📍 Événement: {result['event_type']} - {result['event_subtype']}")
    print(f"🎯 Méthode de projection: {result['projection_method']}")
    print(f"📊 Entités affectées: {result['affected_sites_count']} sites, {result['affected_suppliers_count']} fournisseurs")
    print(f"⚠️  Niveau de risque global: {result['overall_risk_level']}")
    
    print("\n🏭 Sites affectés:")
    for site in result['affected_sites'][:3]:  # Top 3
        print(f"  - {site['name']}: {site['distance_km']} km (impact: {site['impact_level']})")
    
    print("\n🏢 Fournisseurs affectés:")
    for sup in result['affected_suppliers'][:3]:  # Top 3
        print(f"  - {sup['name']}: {sup['distance_km']} km (impact: {sup['impact_level']})")
    
    print("\n🔍 Analyse de criticité:")
    for site_crit in result['criticality_analysis']['sites'][:2]:
        print(f"  Site: {site_crit['entity_name']}")
        print(f"    Criticité: {site_crit['overall_criticality']}")
        print(f"    Urgence: {site_crit['urgency_level']}/5")
        print(f"    Impact supply chain: {site_crit['supply_chain_impact']}")
    
    print("\n💡 Recommandations:")
    print(result['recommendations'])
    
    return result


def test_reglementaire():
    """Test avec événement réglementaire (CBAM)"""
    print_separator("TEST 2: ÉVÉNEMENT RÉGLEMENTAIRE - CBAM Phase 2")
    
    agent = Agent2()
    
    result = agent.analyze(
        document=MOCK_DOCUMENTS["reglementaire"],
        pertinence_result=MOCK_PERTINENCE_RESULTS["reglementaire"],
        sites=MOCK_SITES,
        suppliers=MOCK_SUPPLIERS,
        supplier_relationships=MOCK_RELATIONSHIPS
    )
    
    print(f"📍 Événement: {result['event_type']} - {result['event_subtype']}")
    print(f"🎯 Méthode de projection: {result['projection_method']}")
    print(f"📊 Entités affectées: {result['affected_sites_count']} sites, {result['affected_suppliers_count']} fournisseurs")
    print(f"⚠️  Niveau de risque global: {result['overall_risk_level']}")
    
    print("\n🏭 Sites affectés:")
    for site in result['affected_sites']:
        print(f"  - {site['name']}")
        print(f"    Critères: {', '.join(site['matching_criteria'])}")
        print(f"    Impact: {site['impact_level']}")
    
    print("\n💡 Recommandations:")
    print(result['recommendations'])
    
    return result


def test_geopolitique():
    """Test avec événement géopolitique (conflit Ukraine)"""
    print_separator("TEST 3: ÉVÉNEMENT GÉOPOLITIQUE - Conflit Ukraine")
    
    agent = Agent2()
    
    result = agent.analyze(
        document=MOCK_DOCUMENTS["geopolitique"],
        pertinence_result=MOCK_PERTINENCE_RESULTS["geopolitique"],
        sites=MOCK_SITES,
        suppliers=MOCK_SUPPLIERS,
        supplier_relationships=MOCK_RELATIONSHIPS
    )
    
    print(f"📍 Événement: {result['event_type']} - {result['event_subtype']}")
    print(f"🎯 Méthode de projection: {result['projection_method']}")
    print(f"📊 Entités affectées: {result['affected_sites_count']} sites, {result['affected_suppliers_count']} fournisseurs")
    print(f"⚠️  Niveau de risque global: {result['overall_risk_level']}")
    
    print("\n🏢 Fournisseurs affectés:")
    for sup in result['affected_suppliers']:
        print(f"  - {sup['name']}")
        print(f"    Facteurs de risque: {', '.join(sup['risk_factors'])}")
        print(f"    Impact: {sup['impact_level']}")
    
    print("\n💡 Recommandations:")
    print(result['recommendations'])
    
    return result


def save_results_to_json(results: dict, filename: str):
    """Sauvegarde les résultats en JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Résultats sauvegardés dans {filename}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n🚀 TESTS AGENT 2 - RISK ANALYZER\n")
    
    # Test 1: Climatique
    result1 = test_climatique()
    
    # Test 2: Réglementaire
    result2 = test_reglementaire()
    
    # Test 3: Géopolitique
    result3 = test_geopolitique()
    
    # Sauvegarder les résultats
    all_results = {
        "climatique": result1,
        "reglementaire": result2,
        "geopolitique": result3
    }
    
    save_results_to_json(all_results, "agent_2_test_results.json")
    
    print_separator("TESTS TERMINÉS")
    print("✅ Tous les tests ont été exécutés avec succès!")
    print("\n📝 Résumé:")
    print(f"  - Test climatique: {result1['affected_sites_count']} sites, {result1['affected_suppliers_count']} fournisseurs")
    print(f"  - Test réglementaire: {result2['affected_sites_count']} sites, {result2['affected_suppliers_count']} fournisseurs")
    print(f"  - Test géopolitique: {result3['affected_sites_count']} sites, {result3['affected_suppliers_count']} fournisseurs")
