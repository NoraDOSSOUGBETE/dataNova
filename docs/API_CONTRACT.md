# 📋 Contrat d'API Backend - Plateforme Veille Réglementaire

> **Source** : Copié depuis la branche `frontend` (README.md)  
> **Date** : 23/01/2026  
> **Version** : 1.0.0

---

## 🎯 Objectif

Ce document définit le **contrat d'interface** entre le frontend et le backend. 

⚠️ **Le backend DOIT respecter EXACTEMENT ce contrat** pour assurer la compatibilité avec le frontend.

---

## 🌐 Configuration

### Base URL
```
http://localhost:8000/api
```

### CORS
Le backend doit accepter les requêtes depuis :
- `http://localhost:3000`
- `http://localhost:3005`
- `http://localhost:5173`

---

## 📡 Endpoints Requis

### 1️⃣ **Liste des réglementations**

```http
GET /api/regulations
```

**Query Parameters** :
| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `status` | string | Non | `all`, `pending`, `validated`, `rejected`, `to-review` |
| `search` | string | Non | Recherche dans le titre |
| `page` | number | Non | Numéro de page (défaut: 1) |
| `limit` | number | Non | Résultats par page (défaut: 10) |

**Response** (200 OK) :
```json
{
  "regulations": [
    {
      "id": "uuid",
      "title": "Regulation (EU) 2023/956 - CBAM",
      "description": "Carbon Border Adjustment Mechanism...",
      "status": "pending",
      "type": "regulation",
      "dateCreated": "2026-01-10T14:30:00Z",
      "reference": "https://eur-lex.europa.eu/..."
    }
  ],
  "total": 245,
  "page": 1,
  "limit": 10
}
```

---

### 2️⃣ **Détails d'une réglementation**

```http
GET /api/regulations/:id
```

**Response** (200 OK) :
```json
{
  "id": "uuid",
  "title": "Regulation (EU) 2023/956 - CBAM",
  "description": "Carbon Border Adjustment Mechanism...",
  "status": "pending",
  "type": "regulation",
  "dateCreated": "2026-01-10T14:30:00Z",
  "reference": "https://eur-lex.europa.eu/..."
}
```

**Errors** :
- `404 Not Found` : Réglementation inexistante

---

### 3️⃣ **Mettre à jour le statut**

```http
PUT /api/regulations/:id/status
```

**Request Body** :
```json
{
  "status": "validated",
  "comment": "Réglementation validée après analyse"
}
```

**Status possibles** :
- `validated` : Validée par l'équipe juridique
- `rejected` : Rejetée (non pertinente)
- `to-review` : À réviser

**Response** (200 OK) :
```json
{
  "id": "uuid",
  "title": "Regulation (EU) 2023/956 - CBAM",
  "description": "Carbon Border Adjustment Mechanism...",
  "status": "validated",
  "type": "regulation",
  "dateCreated": "2026-01-10T14:30:00Z",
  "reference": "https://eur-lex.europa.eu/..."
}
```

**Errors** :
- `404 Not Found` : Réglementation inexistante
- `400 Bad Request` : Status invalide

---

### 4️⃣ **Statistiques**

```http
GET /api/regulations/stats
```

**Response** (200 OK) :
```json
{
  "total": 245,
  "by_status": {
    "pending": 123,
    "validated": 98,
    "rejected": 24
  },
  "recent_count": 15,
  "high_priority": 7
}
```

---

## 📦 Types de données

### Regulation

```typescript
interface Regulation {
  id: string;                  // UUID de la réglementation
  title: string;               // Titre de la réglementation
  description: string;         // Description/résumé
  status: 'pending' | 'validated' | 'rejected' | 'to-review';
  type: string;                // Type de réglementation
  dateCreated: Date;           // Date de création
  reference?: string;          // URL de référence (optionnel)
}
```

### RegulationListResponse

```typescript
interface RegulationListResponse {
  regulations: Regulation[];   // ⚠️ Clé importante : "regulations" (pas "data")
  total: number;               // Nombre total de réglementations
  page: number;                // Page actuelle
  limit: number;               // Résultats par page
}
```

### UpdateRegulationRequest

```typescript
interface UpdateRegulationRequest {
  status: 'validated' | 'rejected' | 'to-review';
  comment?: string;            // Optionnel
}
```

---

## ⚠️ Points critiques

### ✅ À respecter absolument

1. **Clé de réponse** : Utiliser `"regulations"` (PAS `"data"`)
2. **Status values** : 
   - Frontend utilise : `pending`, `validated`, `rejected`, `to-review`
   - Si backend utilise d'autres valeurs, faire un mapping
3. **Base URL** : `/api` (PAS `/api/v1`)
4. **Format dates** : ISO 8601 (`2026-01-10T14:30:00Z`)

---

## 🔄 Mapping des statuts (si nécessaire)

Si votre backend utilise des statuts différents :

| Frontend | Backend (exemple) |
|----------|-------------------|
| `to-review` | `pending` |
| `validated` | `approved` |
| `rejected` | `rejected` |
| `pending` | `pending` |

---

## 🧪 Comment tester la conformité

### 1. Démarrer l'API
```bash
uvicorn src.api.main:app --reload --port 8000
```

### 2. Tester les endpoints
```bash
# Liste
curl http://localhost:8000/api/regulations

# Avec filtres
curl "http://localhost:8000/api/regulations?status=pending&page=1&limit=10"

# Détails
curl http://localhost:8000/api/regulations/{id}

# Update status
curl -X PUT http://localhost:8000/api/regulations/{id}/status \
  -H "Content-Type: application/json" \
  -d '{"status": "validated", "comment": "OK"}'

# Stats
curl http://localhost:8000/api/regulations/stats
```

### 3. Vérifier la documentation Swagger
```
http://localhost:8000/docs
```

---

## 📋 Checklist de conformité

- [x] Base URL `/api`
- [x] GET `/api/regulations` (avec filtres)
- [x] GET `/api/regulations/:id`
- [x] PUT `/api/regulations/:id/status`
- [x] GET `/api/regulations/stats`
- [x] Clé de réponse `regulations`
- [x] Status mapping correct
- [x] Structure Regulation conforme
- [x] Pagination (total, page, limit)
- [x] CORS configuré

---

## 📞 Contact

- **Frontend** : Narjiss
- **Backend** : Khadidja
- **Repository** : PING-DataNova/backend_dataNova

---

**Version** : 1.0.0  
**Dernière mise à jour** : 23/01/2026
