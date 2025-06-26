# 🚀 SoGood - Guide de démarrage rapide

## 📋 Prérequis

- **Python 3.10+**
- **Docker Desktop**
- **Git**

## ⚡ Démarrage rapide

### 1. Cloner le projet
```bash
git clone <repository-url>
cd sogood-nutritional-analysis
```

### 2. Démarrer Cassandra
```bash
# Démarrer Cassandra avec Docker
docker-compose up -d cassandra
```

### 3. Initialiser la base de données
```bash
# Initialiser Cassandra
python scripts/init_cassandra.py
```

### 4. Charger les données
```bash
# Charger les données (optionnel)
python scripts/load_data.py --max-rows 1000
```

### 5. Démarrer l'API
```bash
# Démarrer l'API FastAPI
docker-compose up -d api
```

### 6. Démarrer le frontend
```bash
# Démarrer l'application web
cd frontend/web_app
python app.py
```

## 🌐 Accès aux services

- **Frontend**: http://localhost:5000
- **API Backend**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **Cassandra**: localhost:9042

## 🔧 Scripts de démarrage automatique

### Linux/Mac
```bash
./start.sh
```

### Windows
```powershell
.\start.ps1
```

## 📊 Vérification

### Vérifier que Cassandra fonctionne
```bash
docker-compose exec cassandra cqlsh -e "SELECT release_version FROM system.local;"
```

### Vérifier que l'API répond
```bash
curl http://localhost:8000/health
```

### Vérifier le frontend
Ouvrez http://localhost:5000 dans votre navigateur

## 🛠️ Dépannage

### Erreur Cassandra
```bash
# Redémarrer Cassandra
docker-compose restart cassandra

# Vérifier les logs
docker-compose logs cassandra
```

### Erreur API
```bash
# Redémarrer l'API
docker-compose restart api

# Vérifier les logs
docker-compose logs api
```

### Erreur de connexion
```bash
# Vérifier que tous les services sont démarrés
docker-compose ps

# Redémarrer tous les services
docker-compose down
docker-compose up -d
```

## 📚 Documentation complète

- [README.md](README.md) - Documentation principale
- [TEAM_SETUP.md](TEAM_SETUP.md) - Guide d'équipe
- [API Documentation](http://localhost:8000/docs) - Documentation interactive de l'API

## 🆘 Support

En cas de problème :
1. Vérifiez les logs : `docker-compose logs`
2. Consultez la documentation
3. Ouvrez une issue sur GitHub 