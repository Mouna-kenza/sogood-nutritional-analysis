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

# Vérifier Python 3.10+
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
# Démarrer Cassandra + Backend API
docker-compose up -d

# Vérifier que tout fonctionne
docker ps
```

**Résultat attendu :**
- `sogood_cassandra` : Base de données Cassandra (port 9042)
- `sogood_api` : API FastAPI (port 8000)

### 2. Initialiser Cassandra
```bash
# Initialiser les tables Cassandra
python scripts/init_cassandra.py
```

### 3. Charger les Données
```bash
# Charger les produits dans la base
python scripts/load_data.py
```

---

## 🔧 Démarrage Manuel (Développement)

### Option A : Backend + Base de Données Docker
```bash
# 1. Démarrer seulement Cassandra
docker-compose up -d cassandra

# 2. Initialiser Cassandra
python scripts/init_cassandra.py

# 3. Démarrer le backend en local
python backend/main.py
```

### Option B : Tout en Local
```bash
# 1. Installer Cassandra localement
# 2. Créer le keyspace 'sogood'
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
# Accès à Cassandra
docker exec -it sogood_cassandra cqlsh

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
docker exec sogood_cassandra cqlsh -e "SELECT COUNT(*) FROM sogood.products;"
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
docker exec -it sogood_cassandra cqlsh

# Sauvegarder (optionnel)
# Cassandra ne nécessite pas de sauvegarde traditionnelle
# Les données sont répliquées automatiquement

# Vérifier l'état
docker exec sogood_cassandra nodetool status
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
# Vérifier que Cassandra tourne
docker ps | grep cassandra

# Vérifier les logs
docker logs sogood_cassandra

# Redémarrer Cassandra
docker-compose restart cassandra
```

### Problème de Données
```bash
# Vérifier les tables
docker exec sogood_cassandra cqlsh -e "DESCRIBE KEYSPACES;"
docker exec sogood_cassandra cqlsh -e "USE sogood; DESCRIBE TABLES;"

# Recharger les données
python scripts/load_data.py --max-rows 1000
```

### Problème API
```bash
# Vérifier les logs
docker logs sogood_api

# Redémarrer l'API
docker-compose restart api

# Test de connexion
curl http://localhost:8000/health
```

---

## 📊 Monitoring

### État des Services
```bash
# Vérifier tous les services
docker-compose ps

# Logs en temps réel
docker-compose logs -f --tail=100
```

### Métriques Cassandra
```bash
# État du cluster
docker exec sogood_cassandra nodetool status

# Statistiques
docker exec sogood_cassandra nodetool info
```

### Métriques API
```bash
# Health check
curl http://localhost:8000/health

# Statistiques
curl http://localhost:8000/api/products/stats
```

---

## 🔄 Workflow de Développement

### 1. Développement Backend
```bash
# Modifier le code
# backend/models/
# backend/controllers/
# backend/services/

# Tester les changements
docker-compose restart api
curl http://localhost:8000/health
```

### 2. Développement Frontend
```bash
# Modifier les templates
# frontend/web_app/templates/

# Redémarrer le frontend
cd frontend/web_app
python app.py
```

### 3. Tests de Données
```bash
# Charger des données de test
python scripts/load_data.py --max-rows 100

# Tester les requêtes
curl "http://localhost:8000/api/products/search?q=test"
```

---

## 📈 Performance

### Optimisations Cassandra
- **Clés de partition** : Optimisées pour les requêtes fréquentes
- **Réplication** : 3 copies par défaut
- **Compression** : LZ4 activée

### Optimisations API
- **Cache** : Redis (optionnel)
- **Pagination** : Limite par défaut 20 produits
- **Filtres** : Indexés sur les champs fréquents

---

## 🎯 Prochaines Étapes

### Phase 1 : Base Solide ✅
- [x] Infrastructure Cassandra
- [x] API FastAPI
- [x] Frontend Flask
- [x] Chargement des données

### Phase 2 : Fonctionnalités Avancées
- [ ] Recherche avancée
- [ ] Filtres nutritionnels
- [ ] Graphiques et visualisations
- [ ] Système de recommandations

### Phase 3 : Production
- [ ] Monitoring avancé
- [ ] Tests automatisés
- [ ] CI/CD
- [ ] Déploiement cloud

---

## 📞 Support Équipe

### Canaux de Communication
- **Slack** : #sogood-dev
- **Email** : dev@sogood.com
- **GitHub** : Issues et PR

### Documentation
- **API** : http://localhost:8000/docs
- **Code** : README.md dans chaque dossier
- **Architecture** : docs/architecture.md

### Réunions
- **Daily** : 9h00 - Standup
- **Sprint** : Vendredi 14h00 - Rétrospective
- **Architecture** : Mardi 16h00 - Design Review 