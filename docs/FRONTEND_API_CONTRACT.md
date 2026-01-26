# 📡 Contrat API Frontend - Plateforme Veille Réglementaire

## 🎯 Vue d'ensemble

Contrat d'API basé sur l'implémentation actuelle du frontend React/TypeScript.  
**Base URL**: `http://localhost:8000/api`

> ⚠️ **Important**: Cette documentation reflète le contrat attendu par le frontend. Le backend DOIT implémenter ces endpoints exactement comme spécifié.

---

## 📐 Structure TypeScript

### Types de base

```typescript
export interface Regulation {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'validated' | 'rejected' | 'to-review';
  type: string;
  dateCreated: Date;
  reference?: string;
}

export interface User {
  id: string;
  name: string;
  role: 'juridique' | 'decisive';
  avatar?: string;
}
```

### Réponses API

```typescript
export interface RegulationResponse {
  regulations: Regulation[];
  total: number;
  page: number;
  limit: number;
}

export interface UpdateRegulationRequest {
  id: string;
  status: 'validated' | 'rejected' | 'to-review';
  comment?: string;
}
```

---

## 🔐 Authentication

### POST `/auth/login`

**Description**: Authentification utilisateur

**Request Body**:
```json
{
  "email": "juriste@hutchinson.com",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "1",
    "name": "Juriste Hutchinson",
    "email": "juriste@hutchinson.com",
    "role": "juridique"
  }
}
```

**Errors**:
- `401 Unauthorized`: Identifiants invalides
- `400 Bad Request`: Données manquantes

---

### POST `/auth/logout`

**Description**: Déconnexion utilisateur

**Headers**: 
```
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "message": "Déconnexion réussie"
}
```

---

### GET `/auth/me`

**Description**: Récupérer le profil de l'utilisateur connecté

**Headers**:
```
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "id": "1",
  "name": "Juriste Hutchinson",
  "email": "juriste@hutchinson.com",
  "role": "juridique",
  "avatar": "https://..."
}
```

**Errors**:
- `401 Unauthorized`: Token invalide ou expiré

---

## 📋 Réglementations

### GET `/regulations`

**Description**: Liste des réglementations avec filtres

**Headers**:
```
Authorization: Bearer {token}
```

**Query Parameters**:

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `status` | string | Non | `all`, `pending`, `validated`, `rejected`, `to-review` |
| `search` | string | Non | Recherche dans titre/description |
| `page` | number | Non | Numéro de page (défaut: 1) |
| `limit` | number | Non | Résultats par page (défaut: 20) |

**Exemple Request**:
```
GET /api/regulations?status=pending&search=CBAM&page=1&limit=20
```

**Response** (200 OK):
```json
{
  "regulations": [
    {
      "id": "1",
      "title": "Regulation (EU) 2023/956 - CBAM",
      "description": "Carbon Border Adjustment Mechanism...",
      "status": "pending",
      "type": "regulation",
      "dateCreated": "2026-01-10T14:30:00Z",
      "reference": "EU 2023/956"
    }
  ],
  "total": 245,
  "page": 1,
  "limit": 20
}
```

**Errors**:
- `401 Unauthorized`: Token manquant ou invalide
- `400 Bad Request`: Paramètres invalides

**⚠️ Note importante**: 
- La clé principale est `regulations` (pas `data`)
- Le filtrage côté backend est attendu (pas de filtrage frontend)

---

### GET `/regulations/{id}`

**Description**: Récupérer une réglementation spécifique

**Headers**:
```
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "id": "1",
  "title": "Regulation (EU) 2023/956 - CBAM",
  "description": "Carbon Border Adjustment Mechanism...",
  "status": "pending",
  "type": "regulation",
  "dateCreated": "2026-01-10T14:30:00Z",
  "reference": "EU 2023/956"
}
```

**Errors**:
- `404 Not Found`: Réglementation inexistante
- `401 Unauthorized`: Token invalide

---

### PUT `/regulations/{id}/status`

**Description**: Mettre à jour le statut d'une réglementation

**Headers**:
```
Authorization: Bearer {token}
```

**Request Body**:
```json
{
  "status": "validated",
  "comment": "Réglementation validée après analyse"
}
```

**Status possibles**:
- `validated`: Validée par l'équipe juridique
- `rejected`: Rejetée (non pertinente)
- `to-review`: À réviser

**Response** (200 OK):
```json
{
  "id": "1",
  "title": "Regulation (EU) 2023/956 - CBAM",
  "description": "Carbon Border Adjustment Mechanism...",
  "status": "validated",
  "type": "regulation",
  "dateCreated": "2026-01-10T14:30:00Z",
  "reference": "EU 2023/956"
}
```

**Errors**:
- `404 Not Found`: Réglementation inexistante
- `403 Forbidden`: Permissions insuffisantes
- `400 Bad Request`: Status invalide
- `401 Unauthorized`: Token invalide

**⚠️ Différence avec doc API générale**:
- Utilise `PUT /regulations/{id}/status` (endpoint unique)
- Pas de endpoints séparés `/validate` et `/reject`
- Field `comment` optionnel dans le body

---

### GET `/regulations/stats`

**Description**: Récupérer les statistiques des réglementations

**Headers**:
```
Authorization: Bearer {token}
```

**Response** (200 OK):
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

**Errors**:
- `401 Unauthorized`: Token invalide

**⚠️ Note importante**:
- Endpoint: `/regulations/stats` (pas `/dashboard/stats`)
- Structure flexible, adaptée aux besoins du frontend

---

## 🔄 Gestion des Erreurs

### Format standard des erreurs

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Les données fournies sont invalides",
    "details": {
      "field": "status",
      "reason": "Status invalide: 'unknown'"
    }
  },
  "timestamp": "2026-01-23T10:55:00Z"
}
```

### Codes d'erreur HTTP

| Code | Description |
|------|-------------|
| `400` | Bad Request - Paramètres invalides |
| `401` | Unauthorized - Token manquant/invalide |
| `403` | Forbidden - Permissions insuffisantes |
| `404` | Not Found - Ressource inexistante |
| `500` | Internal Server Error - Erreur serveur |

---

## 🔧 Configuration Frontend

### Variables d'environnement

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=10000
VITE_DEBUG=false
```

### Headers par défaut

```typescript
{
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {token}' // Si authentifié
}
```

---

## 📊 Pagination

Format standard pour les listes:

```json
{
  "regulations": [...],
  "total": 245,
  "page": 1,
  "limit": 20
}
```

**Query Parameters**:
- `page`: Numéro de page (défaut: 1)
- `limit`: Résultats par page (défaut: 20)

**⚠️ Différences avec doc API**:
- Pas de champs `total_pages`, `has_next`, `has_previous`
- Structure simplifiée

---

## 🛠️ Implémentation Services

### `src/services/api.ts`

Service de base pour tous les appels API avec:
- Configuration centralisée
- Gestion timeout (10s)
- Gestion erreurs
- Mode debug
- Headers automatiques

### `src/services/regulationsService.ts`

Services spécifiques:
```typescript
regulationsService.getRegulations(filters)
regulationsService.getRegulationById(id)
regulationsService.updateRegulationStatus({ id, status, comment })
regulationsService.getRegulationStats()

authService.login(credentials)
authService.logout()
authService.getCurrentUser()
```

### `src/hooks/useRegulations.ts`

Hooks React pour consommation API:
- `useRegulations(filters)`: Liste avec filtres
- `useRegulationActions()`: Actions (validate, reject)
- Fallback sur mock data si API indisponible

---

## ⚠️ Points critiques d'implémentation Backend

### ✅ À respecter absolument

1. **Base URL**: `/api` (PAS `/api/v1`)
2. **Clé réponse**: `regulations` (PAS `data`)
3. **Status values**: Inclure `to-review` (en plus de `pending`)
4. **Endpoint status**: `PUT /regulations/{id}/status` (endpoint unique)
5. **Endpoint stats**: `/regulations/stats` (PAS `/dashboard/stats`)
6. **Endpoint user**: `/auth/me` (à ajouter)

### ⚙️ Différences avec documentation API générale

| Aspect | Doc API générale | Frontend actuel |
|--------|------------------|-----------------|
| Base URL | `/api/v1` | `/api` |
| Clé réponse | `data` | `regulations` |
| Update endpoint | `/validate` + `/reject` | `/status` (unique) |
| Stats endpoint | `/dashboard/stats` | `/regulations/stats` |
| Status pending | `pending` | `pending` + `to-review` |

---

## 🧪 Mode Développement

Le frontend inclut un **système de fallback** automatique:
- Si API indisponible → Utilisation de **mock data**
- Affichage d'un message: `"Mode démo - Backend non connecté"`
- Permet développement frontend sans backend actif

**Mock data location**: `src/data/mockData.ts`

---

## 📞 Checklist Backend

Avant de connecter le frontend, vérifier que le backend implémente:

- [ ] ✅ Base URL: `/api` (sans `/v1`)
- [ ] ✅ Endpoint: `POST /auth/login`
- [ ] ✅ Endpoint: `POST /auth/logout`
- [ ] ✅ Endpoint: `GET /auth/me`
- [ ] ✅ Endpoint: `GET /regulations` (avec filtres `status`, `search`, `page`, `limit`)
- [ ] ✅ Endpoint: `GET /regulations/{id}`
- [ ] ✅ Endpoint: `PUT /regulations/{id}/status` (body: `{ status, comment }`)
- [ ] ✅ Endpoint: `GET /regulations/stats`
- [ ] ✅ Réponse: clé `regulations` (pas `data`)
- [ ] ✅ Status: support de `to-review` en plus de `pending`
- [ ] ✅ CORS: Autoriser origine frontend
- [ ] ✅ Headers: Support de `Authorization: Bearer {token}`

---

## 🔗 Références

- **Types TypeScript**: [`src/types/index.ts`](../src/types/index.ts)
- **Services API**: [`src/services/regulationsService.ts`](../src/services/regulationsService.ts)
- **Configuration**: [`src/services/api.ts`](../src/services/api.ts)
- **Hooks**: [`src/hooks/useRegulations.ts`](../src/hooks/useRegulations.ts)

---

**Version**: 1.0.0  
**Dernière mise à jour**: 23/01/2026  
**Basé sur**: Implementation frontend actuelle  
**Contact**: dev@hutchinson.com
