# sogood-nutritional-analysis
🥗 Analyse nutritionnelle des produits alimentaires avec Cassandra, FastAPI et Power BI - Projet étudiant

## 🎯 Objectif du Projet
Analyser la qualité nutritionnelle des produits alimentaires français en utilisant les données OpenFoodFacts avec des technologies Big Data et Machine Learning.

**Durée :** 5 jours (Lundi → Vendredi)  
**Dataset :** [OpenFoodFacts France]([https://fr.openfoodfacts.org/](https://www.data.gouv.fr/fr/datasets/open-food-facts-produits-alimentaires-ingredients-nutrition-labels/)) - 200k+ produits

## 👥 Équipe & Responsabilités

### 🎨 **Mouna** - Frontend & Business Intelligence
- **📁 Dossier :** `frontend/`
- **🛠️ Technologies :** Flask, Power BI, Bootstrap, Plotly
- **📋 Tâches :**
  - Interface web de recherche produits
  - Pages de détail nutritionnel
  - 3 dashboards Power BI analytics
  - Design UX/UI responsive

### 🔧 **Giscard** - Infrastructure & Base de Données
- **📁 Dossier :** `backend/database/`
- **🛠️ Technologies :** Cassandra, FastAPI, cqlengine
- **📋 Tâches :**
  - Setup base de données Cassandra
  - Schémas tables produits
  - APIs backend pour frontend
  - Pipeline ingestion données

### ⚡ **Yasser** - Big Data & Machine Learning  
- **📁 Dossier :** `backend/pyspark/`
- **🛠️ Technologies :** PySpark, Scikit-learn, Pandas
- **📋 Tâches :**
  - Traitement dataset OpenFoodFacts
  - Algorithmes calcul Nutri-Score
  - Classification NOVA (1-4)
  - Détection controverses nutritionnelles

## 🏗️ Architecture du Système
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Analytics     │
│   (Mouna)       │    │   (Giscard)     │    │   (Yasser)      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Flask Web App │◄──►│ • Cassandra DB  │◄──►│ • PySpark Jobs  │
│ • Power BI      │    │ • FastAPI REST  │    │ • ML Models     │
│ • Dashboards    │    │ • cqlengine ORM │    │ • Algorithmes   │
│ • Interface     │    │ • Data Storage  │    │ • Calculs       │
└─────────────────┘    └─────────────────┘    └─────────────────┘

## 📊 Fonctionnalités Prévues

### ✅ **Core Features**
- 🔍 **Recherche produits** par nom, marque, catégorie, code-barres
- 🏷️ **Affichage Nutri-Score** avec code couleur (A→E)
- 📋 **Fiche produit détaillée** : nutrition, additifs, controverses
- ⚖️ **Comparateur** de produits similaires
- 📊 **Analytics** : tendances nutritionnelles par catégorie/marque

### 📈 **Power BI Dashboards**
1. **Vue d'ensemble** : Distribution Nutri-Score, KPIs globaux
2. **Analyse par catégorie** : Comparaisons, moyennes nutritionnelles  
3. **Détection controverses** : Alertes sucre/sel/additifs

### 🤖 **Intelligence**
- 🧮 **Calcul automatique** Nutri-Score selon algorithme officiel
- 🔢 **Classification NOVA** (niveau transformation industrielle)
- ⚠️ **Détection controverses** : seuils sucre, sel, additifs dangereux
- 🎯 **Prédictions ML** : qualité nutritionnelle nouveaux produits

## 🚀 Quick Start

### Prérequis
- Docker et Docker Compose
- Python 3.8+

### Installation
```bash
# Cloner le projet
git clone <repository>
cd sogood-nutritional-analysis

# Copier le fichier d'environnement
cp env.example .env

# Démarrer les services
docker-compose up -d

# Initialiser Cassandra
python scripts/init_cassandra.py

# Charger les données
python scripts/load_data.py
```

### Services
- **Frontend** : http://localhost:5000
- **API Backend** : http://localhost:8000
- **Cassandra** : localhost:9042

## 📅 Planning de Développement

| Jour | Mouna (Frontend) | Giscard (Backend) | Yasser (Analytics) |
|------|------------------|-------------------|-------------------|
| **Lundi** | Setup Flask + maquettes | Setup Cassandra + schémas | Exploration dataset |
| **Mardi** | Interface recherche | FastAPI + ingestion | Algorithmes Nutri-Score |
| **Mercredi** | Power BI dashboards | Intégration frontend | ML + controverses |
| **Jeudi** | Polish UI + tests | Optimisations | Intégration finale |
| **Vendredi** | **🎯 DÉMO FINALE** | **�� DÉMO FINALE** | **🎯 DÉMO FINALE** |

## 🚀 Démarrage rapide

### 1. Lancer Cassandra et l'API backend (Docker)
```sh
docker-compose up -d
```

### 2. Lancer le backend (API FastAPI) en local (hors Docker)
```sh
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Lancer le frontend Flask
```sh
cd frontend/web_app
python app.py
```

### 4. Vérifier l'API
```sh
curl http://localhost:8000/health
```
Ou ouvrir http://localhost:8000/docs dans le navigateur.

### 5. (Optionnel) Exporter un CSV pour Power BI
```sh
cd frontend/power_bi
python export_data.py
```
Ou utiliser le bouton « Exporter CSV » sur la page `/dashboard` du frontend.

### 6. Arrêter les services Docker
```sh
docker-compose down
```

---

**Résumé :**
- `docker-compose up -d` (Cassandra + API)
- `cd backend && uvicorn main:app --reload` (API en dev)
- `cd frontend/web_app && python app.py` (Frontend Flask)
- `cd frontend/power_bi && python export_data.py` (Export CSV)

---

Pour toute question ou problème, voir la documentation détaillée ou contacter l'équipe.

