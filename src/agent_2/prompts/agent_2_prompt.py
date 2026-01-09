"""
Prompt principal pour Agent 2

TODO (Dev 4): Définir le prompt complet

Le prompt doit inclure :
- Rôle et responsabilités de l'Agent 2
- Instructions d'analyse d'impact
- Format de sortie attendu
- Critères de scoring
- Guidelines pour recommandations
"""

from langchain.prompts import PromptTemplate


# TODO: Définir le prompt complet
AGENT_2_PROMPT = PromptTemplate.from_template(
    """Tu es l'Agent 2, spécialisé dans l'analyse d'impact réglementaire.

TODO (Dev 4): Compléter ce prompt avec :
- Instructions détaillées
- Variables dynamiques (company_profile, analysis, etc.)
- Format de sortie structuré
- Exemples

Question: {input}
{agent_scratchpad}
"""
)
