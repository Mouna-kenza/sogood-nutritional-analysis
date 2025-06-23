# sogood-nutritional-analysis
🥗 Analyse nutritionnelle des produits alimentaires avec PySpark, Airflow et Power BI - Projet étudiant

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
- **🛠️ Technologies :** PostgreSQL/MySQL, APIs REST
- **📋 Tâches :**
  - Setup base de données
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
│ • Flask Web App │◄──►│ • Base Données  │◄──►│ • PySpark Jobs  │
│ • Power BI      │    │ • APIs REST     │    │ • ML Models     │
│ • Dashboards    │    │ • ETL Pipeline  │    │ • Algorithmes   │
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

## 📅 Planning de Développement

| Jour | Mouna (Frontend) | Giscard (Backend) | Yasser (Analytics) |
|------|------------------|-------------------|-------------------|
| **Lundi** | Setup Flask + maquettes | Choix BDD + schémas | Exploration dataset |
| **Mardi** | Interface recherche | APIs + ingestion | Algorithmes Nutri-Score |
| **Mercredi** | Power BI dashboards | Intégration frontend | ML + controverses |
| **Jeudi** | Polish UI + tests | Optimisations | Intégration finale |
| **Vendredi** | **🎯 DÉMO FINALE** | **🎯 DÉMO FINALE** | **🎯 DÉMO FINALE** |

