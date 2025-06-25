# 🚀 Guide de Démarrage Équipe - SoGood

## 👥 Pour l'Équipe de Développement

Ce guide explique comment démarrer le projet SoGood pour travailler en équipe sur les différentes parties (Frontend, Backend, Base de Données).

---

## 📋 Prérequis

### 1. Installation des Outils
```bash
# Vérifier que Docker est installé
docker --version
docker-compose --version

# Vérifier Python 3.8+
python --version

# Installer les dépendances Python
pip install -r requirements.txt
```

### 2. Fichier de Configuration
```bash
# Copier le fichier d'environnement
cp env.example .env
```

---

## 🐳 Démarrage avec Docker (Recommandé)

### 1. Démarrer l'Infrastructure Complète
```bash
# Démarrer PostgreSQL + Backend API
docker-compose up -d

# Vérifier que tout fonctionne
docker ps
```

**Résultat attendu :**
- `sogood_postgres` : Base de données PostgreSQL (port 5432)
- `sogood_api` : API FastAPI (port 8000)

### 2. Charger les Données
```bash
# Charger les produits dans la base (999 produits uniques)
python scripts/load_data.py
```

---

## 🔧 Démarrage Manuel (Développement)

### Option A : Backend + Base de Données Docker
```bash
# 1. Démarrer seulement PostgreSQL
docker-compose up -d postgres

# 2. Démarrer le backend en local
python backend/main.py
```

### Option B : Tout en Local
```bash
# 1. Installer PostgreSQL localement
# 2. Créer la base 'sogood_db'
# 3. Modifier .env avec les bonnes connexions
# 4. Démarrer le backend
python backend/main.py
```

---

## 🌐 Démarrage du Frontend

### 1. Démarrer le Frontend Flask
```bash
# Utiliser le script de démarrage
python start_frontend.py

# Ou manuellement
cd frontend/web_app
python app.py
```

### 2. Accéder à l'Application
- **Frontend** : http://localhost:5000
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

---

## 🎯 Rôles et Accès

### 👨‍💻 **Giscard - Backend & Base de Données**
```bash
# Accès à la base de données
docker exec -it sogood_postgres psql -U sogood_user -d sogood_db

# Logs du backend
docker logs sogood_api

# Redémarrer le backend
docker-compose restart api
```

### 🎨 **Mouna - Frontend & Interface**
```bash
# Démarrer le frontend
python start_frontend.py

# Modifier les templates
# frontend/web_app/templates/
# frontend/web_app/static/
```

### ⚡ **Yasser - Analytics & ML**
```bash
# Accès aux notebooks
cd notebooks/

# Données brutes
ls data/raw/

# Scripts d'analyse
python scripts/analyze_data_quality.py
```

---

## 🔍 Vérification du Fonctionnement

### 1. Test de la Base de Données
```bash
# Vérifier les produits chargés
docker exec sogood_postgres psql -U sogood_user -d sogood_db -c "SELECT COUNT(*) FROM products;"
```

### 2. Test de l'API Backend
```bash
# Test de santé
curl http://localhost:8000/health

# Recherche de produits
curl "http://localhost:8000/api/products/search?q=nutella&page=1"
```

### 3. Test du Frontend
- Ouvrir http://localhost:5000
- Rechercher "Nutella" ou "Evian"
- Vérifier l'affichage des produits

---

## 🛠️ Commandes Utiles

### Gestion Docker
```bash
# Voir les logs
docker-compose logs -f

# Redémarrer tout
docker-compose down && docker-compose up -d

# Nettoyer
docker-compose down -v
```

### Base de Données
```bash
# Connexion directe
docker exec -it sogood_postgres psql -U sogood_user -d sogood_db

# Sauvegarder
docker exec sogood_postgres pg_dump -U sogood_user sogood_db > backup.sql

# Restaurer
docker exec -i sogood_postgres psql -U sogood_user -d sogood_db < backup.sql
```

### Développement
```bash
# Recharger les données
python scripts/load_data.py

# Analyser la qualité des données
python scripts/analyze_data_quality.py

# Optimiser la base
python scripts/optimize_db.py
```

---

## 🚨 Dépannage

### Problème de Connexion Base
```bash
# Vérifier que PostgreSQL tourne
docker ps | grep postgres

# Vérifier les logs
docker logs sogood_postgres

# Redémarrer
docker-compose restart postgres
```

### Problème API
```bash
# Vérifier les logs
docker logs sogood_api

# Redémarrer l'API
docker-compose restart api

# Ou redémarrer manuellement
python backend/main.py
```

### Problème Frontend
```bash
# Vérifier que l'API répond
curl http://localhost:8000/health

# Redémarrer le frontend
python start_frontend.py
```

---

## 📊 Structure des Données

### Tables Principales
- **products** : Informations produits (999 produits uniques)
- **categories** : Catégories hiérarchiques
- **nutritional_values** : Valeurs nutritionnelles
- **quality_scores** : Scores calculés (Nutri-Score, NOVA)

### API Endpoints
- `GET /api/products/search` : Recherche avec filtres
- `GET /api/products/{id}` : Détail produit
- `GET /api/products/stats/database` : Statistiques

---

## 🎯 Workflow de Développement

### 1. **Démarrage Quotidien**
```bash
# 1. Démarrer l'infrastructure
docker-compose up -d

# 2. Vérifier que tout fonctionne
python test_setup.py

# 3. Démarrer le frontend
python start_frontend.py
```

### 2. **Développement Backend (Giscard)**
```bash
# Modifier le code dans backend/
# L'API redémarre automatiquement (hot reload)
```

### 3. **Développement Frontend (Mouna)**
```bash
# Modifier le code dans frontend/web_app/
# Le frontend redémarre automatiquement
```

### 4. **Analytics (Yasser)**
```bash
# Travailler dans notebooks/
# Utiliser les scripts dans scripts/
```

---

## 📞 Support Équipe

### Logs Importants
- **Backend** : `docker logs sogood_api`
- **Base de données** : `docker logs sogood_postgres`
- **Frontend** : Console du navigateur + terminal Flask

### Points de Contact
- **Infrastructure** : Giscard
- **Interface** : Mouna
- **Données** : Yasser

---

## 🎉 C'est Parti !

Une fois tout démarré, vous devriez avoir :
- ✅ Base de données PostgreSQL avec 999 produits
- ✅ API FastAPI accessible sur http://localhost:8000
- ✅ Frontend Flask accessible sur http://localhost:5000
- ✅ Documentation API sur http://localhost:8000/docs

**Bon développement ! 🚀** 