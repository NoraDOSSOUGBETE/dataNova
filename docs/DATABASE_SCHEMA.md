# 🗄️ Schéma de Base de Données - Agent 1

**Projet PING** - Base de données pour la veille réglementaire automatisée

---

## 📊 Architecture Relationnelle

```
┌─────────────────┐
│   documents     │  ← Agent 1A collecte les documents
└────────┬────────┘
         │ 1:N
         │
┌────────▼────────┐
│   analyses      │  ← Agent 1B analyse la pertinence
└────────┬────────┘
         │ 1:N
         │
┌────────▼────────┐
│    alerts       │  ← Notifications générées
└─────────────────┘

┌─────────────────┐    ┌──────────────────┐
│ execution_logs  │    │ company_profiles │  ← Tables indépendantes
└─────────────────┘    └──────────────────┘
```

---

## 📋 Tables Détaillées

### 1️⃣ **documents**

Stocke les documents réglementaires collectés par l'Agent 1A.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id`    | UUID | PRIMARY KEY | Identifiant unique |
| `title` | VARCHAR(500) | NOT NULL | Titre du document |
| `source_url` | VARCHAR(1000) | NOT NULL | URL d'origine (EUR-Lex, etc.) |
| `regulation_type` | VARCHAR(50) | NOT NULL | Type: CBAM, EUDR, CSRD, etc. |
| `publication_date` | DATETIME | NULL | Date de publication officielle |
| `hash_sha256` | VARCHAR(64) | UNIQUE, NOT NULL | Hash SHA-256 du contenu (détection changements) |
| `content` | TEXT | NULL | Texte extrait du PDF |
| `nc_codes` | JSON | NULL | Liste des codes NC trouvés `["4002.19", "7606"]` |
| `metadata` | JSON | NULL | Métadonnées diverses (auteur, type doc, annexes) |
| `status` | VARCHAR(20) | NOT NULL | Statut: `new`, `modified`, `unchanged` |
| `first_seen` | DATETIME | NOT NULL | Date de première détection |
| `last_checked` | DATETIME | NOT NULL | Date de dernière vérification |
| `created_at` | DATETIME | NOT NULL | Date de création en base |

**Index** :
- `idx_documents_hash` sur `hash_sha256` (recherche rapide par hash)
- `idx_documents_status` sur `status` (filtrer nouveaux documents)
- `idx_documents_regulation` sur `regulation_type` (filtrer par type)

**Exemple** :
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Commission Implementing Regulation (EU) 2023/956",
  "source_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R0956",
  "regulation_type": "CBAM",
  "hash_sha256": "a3d5f6e8...",
  "nc_codes": ["7206", "7207", "2710"],
  "status": "new"
}
```

---

### 2️⃣ **analyses**

Résultats d'analyse de pertinence par l'Agent 1B (filtrage 3 niveaux).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Identifiant unique |
| `document_id` | UUID | FOREIGN KEY → documents.id | Document analysé |
| `keyword_match` | BOOLEAN | NOT NULL | Niveau 1 : filtrage par mots-clés passé ? |
| `keyword_score` | FLOAT | NOT NULL | Score mots-clés (0.0 à 1.0) |
| `matched_keywords` | JSON | NULL | Liste des mots-clés trouvés `["carbon", "steel"]` |
| `nc_code_match` | BOOLEAN | NOT NULL | Niveau 2 : filtrage par codes NC passé ? |
| `nc_code_score` | FLOAT | NOT NULL | Score codes NC (0.0 à 1.0) |
| `matched_nc_codes` | JSON | NULL | Codes NC correspondants `["4002.19"]` |
| `llm_score` | FLOAT | NOT NULL | Niveau 3 : score sémantique LLM (0.0 à 1.0) |
| `llm_reasoning` | TEXT | NULL | Explication du LLM (pourquoi pertinent/non pertinent) |
| `total_score` | FLOAT | NOT NULL | Score final pondéré (0.0 à 1.0) |
| `criticality` | VARCHAR(20) | NOT NULL | Criticité: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `relevant` | BOOLEAN | NOT NULL | Document pertinent pour l'entreprise ? |
| `created_at` | DATETIME | NOT NULL | Date de l'analyse |

**Index** :
- `idx_analyses_document` sur `document_id` (jointure avec documents)
- `idx_analyses_relevant` sur `relevant` (filtrer documents pertinents)
- `idx_analyses_criticality` sur `criticality` (trier par criticité)

**Formule score total** :
```
total_score = (keyword_score * 0.3) + (nc_code_score * 0.3) + (llm_score * 0.4)
```

**Mapping criticité** :
- `total_score >= 0.8` → CRITICAL
- `total_score >= 0.6` → HIGH
- `total_score >= 0.4` → MEDIUM
- `total_score < 0.4` → LOW

**Exemple** :
```json
{
  "id": "660f9511-f3ac-52e5-b827-557766551111",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "keyword_match": true,
  "keyword_score": 0.85,
  "matched_keywords": ["carbon", "steel", "imports"],
  "nc_code_match": true,
  "nc_code_score": 1.0,
  "matched_nc_codes": ["7206"],
  "llm_score": 0.92,
  "total_score": 0.89,
  "criticality": "CRITICAL",
  "relevant": true
}
```

---

### 3️⃣ **alerts**

Alertes générées et statut d'envoi.

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Identifiant unique |
| `analysis_id` | UUID | FOREIGN KEY → analyses.id | Analyse source |
| `alert_type` | VARCHAR(50) | NOT NULL | Type: `email`, `webhook`, `slack` |
| `alert_data` | JSON | NOT NULL | Contenu structuré de l'alerte |
| `recipients` | JSON | NOT NULL | Liste des destinataires `["user@example.com"]` |
| `sent_at` | DATETIME | NULL | Date d'envoi (NULL si pas encore envoyé) |
| `status` | VARCHAR(20) | NOT NULL | Statut: `pending`, `sent`, `failed` |
| `error_message` | TEXT | NULL | Message d'erreur si échec d'envoi |
| `created_at` | DATETIME | NOT NULL | Date de création de l'alerte |

**Index** :
- `idx_alerts_analysis` sur `analysis_id` (jointure avec analyses)
- `idx_alerts_status` sur `status` (filtrer alertes en attente)

**Structure `alert_data`** :
```json
{
  "document_title": "Regulation 2023/956",
  "regulation_type": "CBAM",
  "criticality": "CRITICAL",
  "total_score": 0.89,
  "summary": "New CBAM regulation affects steel imports (NC 7206)",
  "recommended_actions": [
    "Review steel import procedures",
    "Calculate CBAM carbon cost"
  ],
  "document_url": "https://..."
}
```

---

### 4️⃣ **execution_logs**

Logs d'exécution des agents (monitoring et debugging).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Identifiant unique |
| `agent_type` | VARCHAR(20) | NOT NULL | Type d'agent: `agent_1a`, `agent_1b` |
| `status` | VARCHAR(20) | NOT NULL | Statut: `success`, `error`, `running` |
| `start_time` | DATETIME | NOT NULL | Début de l'exécution |
| `end_time` | DATETIME | NULL | Fin de l'exécution (NULL si en cours) |
| `duration_seconds` | FLOAT | NULL | Durée totale (calculé) |
| `documents_processed` | INTEGER | DEFAULT 0 | Nombre de documents traités |
| `documents_new` | INTEGER | DEFAULT 0 | Nouveaux documents détectés |
| `documents_modified` | INTEGER | DEFAULT 0 | Documents modifiés détectés |
| `errors` | JSON | NULL | Liste des erreurs rencontrées |
| `metadata` | JSON | NULL | Métadonnées diverses (versions, config, etc.) |
| `created_at` | DATETIME | NOT NULL | Date de création du log |

**Index** :
- `idx_logs_agent` sur `agent_type` (filtrer par agent)
- `idx_logs_status` sur `status` (filtrer erreurs)
- `idx_logs_start_time` sur `start_time` (trier chronologiquement)

**Exemple** :
```json
{
  "id": "770g0622-g4bd-63f6-c938-668877662222",
  "agent_type": "agent_1a",
  "status": "success",
  "start_time": "2026-01-08T10:00:00Z",
  "end_time": "2026-01-08T10:05:23Z",
  "duration_seconds": 323.45,
  "documents_processed": 15,
  "documents_new": 2,
  "documents_modified": 1,
  "errors": [],
  "metadata": {
    "langchain_version": "0.3.0",
    "source": "CBAM"
  }
}
```

---

### 5️⃣ **company_profiles**

Profils entreprise pour le filtrage personnalisé (Agent 1B).

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Identifiant unique |
| `company_name` | VARCHAR(200) | NOT NULL | Nom de l'entreprise |
| `nc_codes` | JSON | NOT NULL | Codes NC pertinents `["4002.19", "7206"]` |
| `keywords` | JSON | NOT NULL | Mots-clés à surveiller `["rubber", "steel"]` |
| `regulations` | JSON | NOT NULL | Réglementations à surveiller `["CBAM", "EUDR"]` |
| `contact_emails` | JSON | NOT NULL | Emails pour alertes `["compliance@company.com"]` |
| `config` | JSON | NULL | Configuration personnalisée (seuils, fréquence) |
| `active` | BOOLEAN | DEFAULT TRUE | Profil actif ou non |
| `created_at` | DATETIME | NOT NULL | Date de création |
| `updated_at` | DATETIME | NOT NULL | Dernière mise à jour |

**Index** :
- `idx_profiles_active` sur `active` (filtrer profils actifs)

**Exemple (AeroRubber Industries)** :
```json
{
  "id": "880h1733-h5ce-74g7-d049-779988773333",
  "company_name": "AeroRubber Industries",
  "nc_codes": ["4002.19", "4002.11"],
  "keywords": ["rubber", "synthetic", "CBAM", "carbon"],
  "regulations": ["CBAM"],
  "contact_emails": ["compliance@aerorubber.com"],
  "config": {
    "min_score_threshold": 0.6,
    "alert_frequency": "immediate"
  },
  "active": true
}
```

---

## 🔗 Relations

```sql
-- documents → analyses (1:N)
ALTER TABLE analyses 
ADD CONSTRAINT fk_analyses_document 
FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE;

-- analyses → alerts (1:N)
ALTER TABLE alerts 
ADD CONSTRAINT fk_alerts_analysis 
FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE;
```
---

## 🛠️ Migrations Alembic

Les migrations seront gérées avec **Alembic** :

```bash
# Créer une migration
alembic revision -m "Initial schema"

# Appliquer les migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 🧪 Données de test

Fichiers JSON de test disponibles dans [`data/`](../data/) :
- `company_profiles/gmg_globex_manufacturing.json`
- `company_profiles/aerorubber_industries.json`
- `suppliers/gmg_suppliers.json`
- `customs_flows/gmg_customs_flows.json`

Ces données seront importées via script d'initialisation pour tester le système.

---

## 📝 Notes techniques

### Choix SQLite vs PostgreSQL

**SQLite** (développement) :
- ✅ Simple, pas de serveur
- ✅ Fichier unique portable
- ❌ Pas de concurrence avancée

**PostgreSQL** (production) :
- ✅ JSONB performant
- ✅ Full-text search
- ✅ Concurrence multi-utilisateurs
- ✅ Robustesse entreprise

Le code SQLAlchemy est compatible avec les deux.

### Types JSON

SQLAlchemy gère automatiquement :
- **SQLite** : TEXT (sérialisation JSON)
- **PostgreSQL** : JSONB (type natif optimisé)

---

## 🔄 Changelog

| Version | Date | Changements |
|---------|------|-------------|
| 0.1.0 | 2026-01-08 | Schéma initial (5 tables) |

---

**Auteur** : Développeur 3 - Agent 1A & Orchestration  
**Projet** : PING DataNova - Agent 1
