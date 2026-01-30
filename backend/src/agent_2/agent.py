"""
Agent 2 - Risk Analyzer

Agent principal qui orchestre l'analyse d'impact complète :
1. Projection (géographique/réglementaire/géopolitique)
2. Analyse de criticité
3. Génération de recommandations avec LLM
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

# Import des moteurs de projection
from .geographic_engine import GeographicEngine
from .regulatory_geopolitical_engine import RegulatoryEngine, GeopoliticalEngine
from .criticality_analyzer import CriticalityAnalyzer
from .llm_reasoning import LLMReasoning


class Agent2:
    """
    Agent 2 - Risk Analyzer
    
    Analyse l'impact d'un événement (réglementaire, climatique, géopolitique)
    sur les sites et fournisseurs Hutchinson.
    """
    
    def __init__(self, llm_model: str = "gemini-2.5-flash"):
        """
        Initialise Agent 2
        
        Args:
            llm_model: Modèle LLM à utiliser pour le raisonnement en cascade
        """
        self.geographic_engine = GeographicEngine()
        self.regulatory_engine = RegulatoryEngine()
        self.geopolitical_engine = GeopoliticalEngine()
        self.criticality_analyzer = CriticalityAnalyzer()
        self.llm_reasoning = LLMReasoning(model=llm_model)
    
    def analyze(
        self,
        document: Dict,
        pertinence_result: Dict,
        sites: List[Dict],
        suppliers: List[Dict],
        supplier_relationships: List[Dict]
    ) -> Dict:
        """
        Analyse complète de l'impact d'un événement.
        
        Args:
            document: Document analysé par Agent 1A
            pertinence_result: Résultat de l'analyse de pertinence (Agent 1B)
            sites: Liste des sites Hutchinson
            suppliers: Liste des fournisseurs
            supplier_relationships: Relations site-fournisseur
            
        Returns:
            Analyse d'impact complète avec recommandations
        """
        event_type = document.get('event_type')
        
        # Étape 1: Projection selon le type d'événement
        if event_type == "climatique":
            projection_result = self._project_climatic_event(document, sites, suppliers)
        elif event_type == "reglementaire":
            projection_result = self._project_regulatory_event(document, sites, suppliers)
        elif event_type == "geopolitique":
            projection_result = self._project_geopolitical_event(document, sites, suppliers)
        else:
            raise ValueError(f"Type d'événement non supporté: {event_type}")
        
        # Étape 2: Analyse de criticité de base
        criticality_results = self._analyze_criticality(
            projection_result,
            sites,
            suppliers,
            supplier_relationships
        )
        
        # Étape 3: Raisonnement LLM en cascade pour chaque entité critique
        cascade_analysis = self._perform_cascade_analysis(
            document,
            projection_result,
            criticality_results,
            supplier_relationships
        )
        
        # Étape 4: Calcul du niveau de risque global (enrichi par LLM)
        overall_risk_level = cascade_analysis.get('overall_risk_level', 
                                                   self._calculate_overall_risk(criticality_results))
        
        # Étape 5: Recommandations (générées par LLM)
        recommendations = cascade_analysis.get('recommendations', [])
        
        # Construire le résultat final
        return {
            "document_id": document.get('id'),
            "event_type": event_type,
            "event_subtype": document.get('event_subtype'),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            
            # Résultats de projection
            "projection_method": projection_result.get('method'),
            "affected_sites": projection_result.get('affected_sites', []),
            "affected_suppliers": projection_result.get('affected_suppliers', []),
            "affected_sites_count": len(projection_result.get('affected_sites', [])),
            "affected_suppliers_count": len(projection_result.get('affected_suppliers', [])),
            
            # Analyse de criticité
            "criticality_analysis": criticality_results,
            "overall_risk_level": overall_risk_level,
            
            # Analyse en cascade (LLM)
            "cascade_analysis": cascade_analysis.get('cascade_details', {}),
            
            # Recommandations
            "recommendations": recommendations,
            
            # Métadonnées
            "geographic_analysis": projection_result.get('geographic_details'),
            "analysis_metadata": {
                "sites_analyzed": len(sites),
                "suppliers_analyzed": len(suppliers),
                "projection_engine": projection_result.get('method'),
                "llm_reasoning_used": self.llm_reasoning.llm_available
            }
        }
    
    def _project_climatic_event(
        self,
        document: Dict,
        sites: List[Dict],
        suppliers: List[Dict]
    ) -> Dict:
        """Projection géographique pour événement climatique"""
        # Extraire les coordonnées de l'événement
        geographic_scope = document.get('geographic_scope', {})
        coordinates = geographic_scope.get('coordinates', {})
        
        if not coordinates or 'latitude' not in coordinates or 'longitude' not in coordinates:
            return {
                "method": "geographic",
                "error": "Coordonnées GPS manquantes",
                "affected_sites": [],
                "affected_suppliers": []
            }
        
        event_lat = coordinates['latitude']
        event_lon = coordinates['longitude']
        
        # Analyser l'impact géographique
        result = self.geographic_engine.analyze_geographic_impact(
            (event_lat, event_lon),
            sites,
            suppliers,
            max_distance_km=200
        )
        
        result['method'] = "geographic"
        result['geographic_details'] = {
            "event_coordinates": (event_lat, event_lon),
            "max_distance_km": 200,
            "impact_zones": GeographicEngine.IMPACT_ZONES
        }
        
        return result
    
    def _project_regulatory_event(
        self,
        document: Dict,
        sites: List[Dict],
        suppliers: List[Dict]
    ) -> Dict:
        """Projection réglementaire pour événement réglementaire"""
        geographic_scope = document.get('geographic_scope', {})
        
        # Extraire les critères réglementaires
        countries = geographic_scope.get('countries', [])
        # On pourrait aussi extraire sectors et products du document
        # Pour l'instant, on utilise ce qui est disponible
        
        if not countries:
            return {
                "method": "regulatory",
                "error": "Pays concernés non spécifiés",
                "affected_sites": [],
                "affected_suppliers": []
            }
        
        # Analyser l'impact réglementaire
        result = self.regulatory_engine.find_affected_by_regulation(
            regulation_countries=countries,
            regulation_sectors=None,  # À extraire du document si disponible
            regulation_products=None,  # À extraire du document si disponible
            sites=sites,
            suppliers=suppliers
        )
        
        result['method'] = "regulatory"
        return result
    
    def _project_geopolitical_event(
        self,
        document: Dict,
        sites: List[Dict],
        suppliers: List[Dict]
    ) -> Dict:
        """Projection géopolitique pour événement géopolitique"""
        geographic_scope = document.get('geographic_scope', {})
        
        # Extraire les pays affectés
        affected_countries = geographic_scope.get('countries', [])
        neighboring_countries = geographic_scope.get('regions', [])  # Approximation
        
        if not affected_countries:
            return {
                "method": "geopolitical",
                "error": "Pays affectés non spécifiés",
                "affected_sites": [],
                "affected_suppliers": []
            }
        
        event_subtype = document.get('event_subtype', 'instabilite')
        
        # Analyser l'impact géopolitique
        result = self.geopolitical_engine.find_affected_by_geopolitical_event(
            affected_countries=affected_countries,
            neighboring_countries=neighboring_countries,
            event_type=event_subtype,
            sites=sites,
            suppliers=suppliers
        )
        
        result['method'] = "geopolitical"
        return result
    
    def _analyze_criticality(
        self,
        projection_result: Dict,
        sites: List[Dict],
        suppliers: List[Dict],
        supplier_relationships: List[Dict]
    ) -> Dict:
        """Analyse la criticité de tous les sites et fournisseurs impactés"""
        criticality_results = {
            "sites": [],
            "suppliers": []
        }
        
        # Analyser les sites
        for affected_site_data in projection_result.get('affected_sites', []):
            site_id = affected_site_data['id']
            impact_level = affected_site_data.get('impact_level', 'moyen')
            
            # Trouver le site complet
            site = next((s for s in sites if s['id'] == site_id), None)
            if site:
                criticality = self.criticality_analyzer.analyze_site_criticality(
                    site,
                    impact_level,
                    sites
                )
                criticality_results['sites'].append({
                    "entity_id": criticality.entity_id,
                    "entity_name": criticality.entity_name,
                    "overall_criticality": criticality.overall_criticality,
                    "supply_chain_impact": criticality.supply_chain_impact,
                    "urgency_level": criticality.urgency_level,
                    "mitigation_options": criticality.mitigation_options,
                    "criticality_factors": criticality.criticality_factors
                })
        
        # Analyser les fournisseurs
        for affected_supplier_data in projection_result.get('affected_suppliers', []):
            supplier_id = affected_supplier_data['id']
            impact_level = affected_supplier_data.get('impact_level', 'moyen')
            
            # Trouver le fournisseur complet
            supplier = next((s for s in suppliers if s['id'] == supplier_id), None)
            if supplier:
                criticality = self.criticality_analyzer.analyze_supplier_criticality(
                    supplier,
                    impact_level,
                    supplier_relationships
                )
                criticality_results['suppliers'].append({
                    "entity_id": criticality.entity_id,
                    "entity_name": criticality.entity_name,
                    "overall_criticality": criticality.overall_criticality,
                    "supply_chain_impact": criticality.supply_chain_impact,
                    "urgency_level": criticality.urgency_level,
                    "mitigation_options": criticality.mitigation_options,
                    "criticality_factors": criticality.criticality_factors
                })
        
        return criticality_results
    
    def _calculate_overall_risk(self, criticality_results: Dict) -> str:
        """Calcule le niveau de risque global"""
        all_criticalities = []
        
        for site in criticality_results.get('sites', []):
            all_criticalities.append(site['overall_criticality'])
        
        for supplier in criticality_results.get('suppliers', []):
            all_criticalities.append(supplier['overall_criticality'])
        
        if not all_criticalities:
            return "faible"
        
        # Si au moins une entité critique
        if "critique" in all_criticalities:
            return "Critique"
        elif "fort" in all_criticalities:
            return "Fort"
        elif "moyen" in all_criticalities:
            return "Moyen"
        else:
            return "Faible"
    
    def _perform_cascade_analysis(
        self,
        document: Dict,
        projection_result: Dict,
        criticality_results: Dict,
        supplier_relationships: List[Dict]
    ) -> Dict:
        """
        Effectue le raisonnement LLM en cascade pour toutes les entités critiques
        
        Returns:
            Dict contenant l'analyse en cascade, le niveau de risque global et les recommandations
        """
        cascade_details = {
            "sites": [],
            "suppliers": []
        }
        
        all_recommendations = []
        max_risk_level = "FAIBLE"
        
        # Analyser les sites critiques/forts
        for site_crit in criticality_results.get('sites', []):
            if site_crit['overall_criticality'] in ['critique', 'fort']:
                # Préparer les relations pour ce site
                site_relationships = [
                    rel for rel in supplier_relationships 
                    if rel.get('site_id') == site_crit['entity_id']
                ]
                
                # Appel LLM pour analyse en cascade
                llm_analysis = self.llm_reasoning.analyze_cascade_impact(
                    event=document,
                    affected_entity=self._find_entity_by_id(site_crit['entity_id'], 'site', projection_result),
                    entity_type="site",
                    relationships=site_relationships,
                    context={"criticality": site_crit}
                )
                
                cascade_details['sites'].append({
                    "entity_id": site_crit['entity_id'],
                    "entity_name": site_crit['entity_name'],
                    "llm_analysis": llm_analysis
                })
                
                # Collecter les recommandations
                if llm_analysis.get('recommendations'):
                    all_recommendations.extend(llm_analysis['recommendations'])
                
                # Mettre à jour le niveau de risque max
                risk_level = llm_analysis.get('overall_risk_level', 'MOYEN')
                if self._risk_level_priority(risk_level) > self._risk_level_priority(max_risk_level):
                    max_risk_level = risk_level
        
        # Analyser les fournisseurs critiques/forts
        for supplier_crit in criticality_results.get('suppliers', []):
            if supplier_crit['overall_criticality'] in ['critique', 'fort']:
                # Préparer les relations pour ce fournisseur
                supplier_relationships_data = [
                    rel for rel in supplier_relationships 
                    if rel.get('supplier_id') == supplier_crit['entity_id']
                ]
                
                # Appel LLM pour analyse en cascade
                llm_analysis = self.llm_reasoning.analyze_cascade_impact(
                    event=document,
                    affected_entity=self._find_entity_by_id(supplier_crit['entity_id'], 'supplier', projection_result),
                    entity_type="supplier",
                    relationships=supplier_relationships_data,
                    context={"criticality": supplier_crit}
                )
                
                cascade_details['suppliers'].append({
                    "entity_id": supplier_crit['entity_id'],
                    "entity_name": supplier_crit['entity_name'],
                    "llm_analysis": llm_analysis
                })
                
                # Collecter les recommandations
                if llm_analysis.get('recommendations'):
                    all_recommendations.extend(llm_analysis['recommendations'])
                
                # Mettre à jour le niveau de risque max
                risk_level = llm_analysis.get('overall_risk_level', 'MOYEN')
                if self._risk_level_priority(risk_level) > self._risk_level_priority(max_risk_level):
                    max_risk_level = risk_level
        
        return {
            "cascade_details": cascade_details,
            "overall_risk_level": max_risk_level,
            "recommendations": all_recommendations
        }
    
    def _find_entity_by_id(self, entity_id: str, entity_type: str, projection_result: Dict) -> Dict:
        """Trouve une entité (site ou fournisseur) par son ID dans les résultats de projection"""
        if entity_type == "site":
            entities = projection_result.get('affected_sites', [])
        else:
            entities = projection_result.get('affected_suppliers', [])
        
        return next((e for e in entities if e.get('id') == entity_id), {})
    
    def _risk_level_priority(self, risk_level: str) -> int:
        """Retourne la priorité d'un niveau de risque (plus élevé = plus critique)"""
        priorities = {
            "FAIBLE": 1,
            "MOYEN": 2,
            "FORT": 3,
            "CRITIQUE": 4
        }
        return priorities.get(risk_level.upper(), 0)
    



# Export
__all__ = ['Agent2']
