# Intégration Frontend - Backend DataNova

## 🎯 Cas d'usage : Équipe juridique valide/rejette une analyse

### Architecture

```
┌─────────────────┐      PUT /api/analyses/{id}/validate       ┌─────────────────┐
│   FRONTEND      │  ────────────────────────────────────────>  │    BACKEND      │
│  (React/Vue)    │  { status: "approved" }                     │   (FastAPI)     │
│                 │  <────────────────────────────────────────  │                 │
│ Équipe Juridique│      Analyse mise à jour                    │ Base de données │
└─────────────────┘                                             └─────────────────┘
```

---

## 📡 API Endpoint

### **PUT /api/analyses/{analysis_id}/validate**

**Description :** Permet à l'équipe juridique d'approuver ou rejeter une analyse

**Paramètres :**
- `analysis_id` (path) : ID de l'analyse à valider
- `status` (query) : `"approved"` ou `"rejected"`

**Exemple de requête :**
```
PUT http://localhost:8000/api/analyses/42/validate?status=approved
```

**Réponse (200 OK) :**
```json
{
  "id": 42,
  "document_id": 15,
  "analysis_text": "Cette réglementation CBAM impacte...",
  "extracted_nc_codes": ["7208", "7209"],
  "countries_affected": ["FR", "DE"],
  "keywords": ["CBAM", "acier"],
  "analysis_metadata": {},
  "validation_status": "approved",
  "created_at": "2026-01-13T10:30:00",
  "updated_at": "2026-01-14T09:15:00"
}
```

**Erreurs possibles :**
- `404` : Analyse non trouvée
- `422` : Status invalide (doit être "approved" ou "rejected")

---

## 💻 Code Frontend

### 1. **Service API** (à créer dans le frontend)

**Fichier : `src/services/analysisApi.ts`** (ou `.js`)

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Récupérer toutes les analyses en attente de validation
export async function getPendingAnalyses() {
  const response = await api.get('/analyses/', {
    params: {
      validation_status: 'pending',
      limit: 100
    }
  });
  return response.data;
}

// Récupérer une analyse par ID
export async function getAnalysis(analysisId: number) {
  const response = await api.get(`/analyses/${analysisId}`);
  return response.data;
}

// Approuver une analyse
export async function approveAnalysis(analysisId: number) {
  const response = await api.put(`/analyses/${analysisId}/validate`, null, {
    params: { status: 'approved' }
  });
  return response.data;
}

// Rejeter une analyse
export async function rejectAnalysis(analysisId: number) {
  const response = await api.put(`/analyses/${analysisId}/validate`, null, {
    params: { status: 'rejected' }
  });
  return response.data;
}

// Récupérer les analyses approuvées
export async function getApprovedAnalyses() {
  const response = await api.get('/analyses/', {
    params: {
      validation_status: 'approved',
      limit: 100
    }
  });
  return response.data;
}

// Récupérer les analyses rejetées
export async function getRejectedAnalyses() {
  const response = await api.get('/analyses/', {
    params: {
      validation_status: 'rejected',
      limit: 100
    }
  });
  return response.data;
}
```

---

### 2. **Composant React** (exemple)

**Fichier : `src/components/LegalValidation.tsx`**

```typescript
import React, { useState, useEffect } from 'react';
import { getPendingAnalyses, approveAnalysis, rejectAnalysis } from '../services/analysisApi';

interface Analysis {
  id: number;
  document_id: number;
  analysis_text: string;
  extracted_nc_codes: string[];
  countries_affected: string[];
  keywords: string[];
  validation_status: string;
  created_at: string;
}

export function LegalValidation() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Charger les analyses en attente au montage du composant
  useEffect(() => {
    loadPendingAnalyses();
  }, []);

  const loadPendingAnalyses = async () => {
    try {
      setLoading(true);
      const data = await getPendingAnalyses();
      setAnalyses(data);
      setError(null);
    } catch (err) {
      setError('Erreur lors du chargement des analyses');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (analysisId: number) => {
    try {
      await approveAnalysis(analysisId);
      
      // Retirer l'analyse de la liste
      setAnalyses(prev => prev.filter(a => a.id !== analysisId));
      
      alert('Analyse approuvée avec succès !');
    } catch (err) {
      alert('Erreur lors de l\'approbation');
      console.error(err);
    }
  };

  const handleReject = async (analysisId: number) => {
    try {
      await rejectAnalysis(analysisId);
      
      // Retirer l'analyse de la liste
      setAnalyses(prev => prev.filter(a => a.id !== analysisId));
      
      alert('Analyse rejetée');
    } catch (err) {
      alert('Erreur lors du rejet');
      console.error(err);
    }
  };

  if (loading) return <div>Chargement...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div className="legal-validation">
      <h1>Validation des analyses - Équipe Juridique</h1>
      
      {analyses.length === 0 ? (
        <p>Aucune analyse en attente de validation</p>
      ) : (
        <div className="analyses-list">
          {analyses.map(analysis => (
            <div key={analysis.id} className="analysis-card">
              <h3>Analyse #{analysis.id}</h3>
              
              <div className="analysis-content">
                <p><strong>Texte :</strong> {analysis.analysis_text}</p>
                <p><strong>Codes NC :</strong> {analysis.extracted_nc_codes.join(', ')}</p>
                <p><strong>Pays affectés :</strong> {analysis.countries_affected.join(', ')}</p>
                <p><strong>Mots-clés :</strong> {analysis.keywords.join(', ')}</p>
                <p><strong>Date :</strong> {new Date(analysis.created_at).toLocaleDateString('fr-FR')}</p>
              </div>

              <div className="actions">
                <button 
                  onClick={() => handleApprove(analysis.id)}
                  className="btn-approve"
                  style={{ backgroundColor: 'green', color: 'white', padding: '10px 20px', marginRight: '10px' }}
                >
                  ✓ Approuver
                </button>
                
                <button 
                  onClick={() => handleReject(analysis.id)}
                  className="btn-reject"
                  style={{ backgroundColor: 'red', color: 'white', padding: '10px 20px' }}
                >
                  ✗ Rejeter
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

### 3. **Composant Vue** (exemple alternatif)

**Fichier : `src/components/LegalValidation.vue`**

```vue
<template>
  <div class="legal-validation">
    <h1>Validation des analyses - Équipe Juridique</h1>
    
    <div v-if="loading">Chargement...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="analyses.length === 0">
      <p>Aucune analyse en attente de validation</p>
    </div>
    
    <div v-else class="analyses-list">
      <div 
        v-for="analysis in analyses" 
        :key="analysis.id" 
        class="analysis-card"
      >
        <h3>Analyse #{{ analysis.id }}</h3>
        
        <div class="analysis-content">
          <p><strong>Texte :</strong> {{ analysis.analysis_text }}</p>
          <p><strong>Codes NC :</strong> {{ analysis.extracted_nc_codes.join(', ') }}</p>
          <p><strong>Pays affectés :</strong> {{ analysis.countries_affected.join(', ') }}</p>
          <p><strong>Mots-clés :</strong> {{ analysis.keywords.join(', ') }}</p>
          <p><strong>Date :</strong> {{ formatDate(analysis.created_at) }}</p>
        </div>

        <div class="actions">
          <button 
            @click="approveAnalysis(analysis.id)"
            class="btn-approve"
          >
            ✓ Approuver
          </button>
          
          <button 
            @click="rejectAnalysis(analysis.id)"
            class="btn-reject"
          >
            ✗ Rejeter
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getPendingAnalyses, approveAnalysis as apiApprove, rejectAnalysis as apiReject } from '../services/analysisApi';

const analyses = ref([]);
const loading = ref(false);
const error = ref(null);

onMounted(() => {
  loadPendingAnalyses();
});

async function loadPendingAnalyses() {
  try {
    loading.value = true;
    analyses.value = await getPendingAnalyses();
    error.value = null;
  } catch (err) {
    error.value = 'Erreur lors du chargement des analyses';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

async function approveAnalysis(analysisId: number) {
  try {
    await apiApprove(analysisId);
    analyses.value = analyses.value.filter(a => a.id !== analysisId);
    alert('Analyse approuvée avec succès !');
  } catch (err) {
    alert('Erreur lors de l\'approbation');
    console.error(err);
  }
}

async function rejectAnalysis(analysisId: number) {
  try {
    await apiReject(analysisId);
    analyses.value = analyses.value.filter(a => a.id !== analysisId);
    alert('Analyse rejetée');
  } catch (err) {
    alert('Erreur lors du rejet');
    console.error(err);
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('fr-FR');
}
</script>

<style scoped>
.analysis-card {
  border: 1px solid #ddd;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
}

.btn-approve {
  background-color: green;
  color: white;
  padding: 10px 20px;
  margin-right: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-reject {
  background-color: red;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.error {
  color: red;
}
</style>
```

---

## 🧪 Tests

### 1. **Démarrer le backend**
```powershell
cd C:\Users\khadi\backend_dataNova
.venv\Scripts\uvicorn src.api.main:app --reload --port 8000
```

### 2. **Tester l'API avec curl ou Postman**

**Approuver une analyse :**
```bash
curl -X PUT "http://localhost:8000/api/analyses/1/validate?status=approved"
```

**Rejeter une analyse :**
```bash
curl -X PUT "http://localhost:8000/api/analyses/1/validate?status=rejected"
```

### 3. **Tester dans Swagger**
Ouvrir : http://localhost:8000/docs
- Chercher `PUT /api/analyses/{analysis_id}/validate`
- Cliquer sur "Try it out"
- Entrer un ID d'analyse et choisir "approved" ou "rejected"
- Cliquer sur "Execute"

---

## 🔐 Sécurité (à ajouter plus tard)

Pour l'instant, l'API est ouverte. Plus tard, vous pourrez ajouter :

1. **Authentification** : Vérifier que l'utilisateur est connecté
2. **Autorisation** : Vérifier que l'utilisateur fait partie de l'équipe juridique
3. **Audit trail** : Logger qui a validé/rejeté quelle analyse

---

## 📋 Résumé des étapes

### Backend (✅ Fait)
- [x] Endpoint `PUT /api/analyses/{id}/validate` créé
- [x] Validation du statut ("approved" ou "rejected")
- [x] Mise à jour de la BDD

### Frontend (À faire)
1. Créer le fichier `services/analysisApi.ts` avec les fonctions d'API
2. Créer le composant `LegalValidation` (React ou Vue)
3. Ajouter une route dans votre router pour `/legal/validation`
4. Tester !

---

## 🚀 Prochaines étapes

1. **Démarrer le backend** : `uvicorn src.api.main:app --reload --port 8000`
2. **Dans le frontend** : Copier le code du service API et du composant
3. **Tester** : Approuver/rejeter des analyses depuis l'interface
4. **Améliorer** : Ajouter l'authentification, les notifications, etc.

Besoin d'aide pour intégrer côté frontend ? 🎯
