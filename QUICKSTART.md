# 🚀 Démarrage Rapide - SoGood

## ✅ Vérification de l'Installation

### 1. Test Automatique
```bash
# Test de l'installation complète
python test_setup.py
```

### 2. Installation des Dépendances
```bash
# Installer les dépendances Python
pip install -r requirements.txt
```

## 🐘 Configuration de la Base de Données

### 1. Créer le fichier de configuration
```bash
# Copier le fichier d'exemple
cp env.example .env
```

### 2. Démarrer PostgreSQL
```bash
# Démarrer PostgreSQL avec Docker
docker-compose up -d postgres
```

## 📊 Chargement des Données

### 1. Test avec un échantillon (recommandé)
```bash
# Charger 1000 produits pour tester
python scripts/load_data.py --max-rows 1000 --batch-size 100
```

### 2. Chargement complet (optionnel)
```bash
# Charger tous les produits (peut prendre du temps)
python scripts/load_data.py --batch-size 2000
```

## 🚀 Démarrage de l'API

### 1. Démarrer l'API FastAPI
```bash
# Démarrer le serveur
python backend/main.py
```

### 2. Accéder à l'API
- **API principale** : http://localhost:8000
- **Documentation** : http://localhost:8000/docs
- **Health check** : http://localhost:8000/health

## 🔗 Intégration avec le Frontend

### 1. Modifier le frontend Flask
```python
# Dans frontend/web_app/app.py, remplacer MOCK_PRODUCTS par :
import requests

API_BASE_URL = "http://localhost:8000/api/v1"

@app.route('/search')
def search():
    response = requests.get(f"{API_BASE_URL}/products/search", params=request.args)
    return response.json()
```

### 2. Démarrer le frontend
```bash
cd frontend/web_app
python app.py
```

## 🧪 Tests Rapides

### 1. Test de l'API
```bash
# Test de santé
curl http://localhost:8000/health

# Test de recherche
curl "http://localhost:8000/api/v1/products/search?q=nutella&page=1&page_size=5"
```

### 2. Test du frontend
- Ouvrir http://localhost:5000
- Rechercher "Nutella" ou "Evian"
- Vérifier que les vraies données s'affichent

## 🛠️ Dépannage

### Erreur PostgreSQL
```bash
# Vérifier que Docker fonctionne
docker ps

# Redémarrer PostgreSQL
docker-compose down
docker-compose up -d postgres
```

### Erreur CSV
```bash
# Vérifier la présence du fichier
ls -la notebooks/fr.openfoodfacts.org.products1.csv  # Fichier nettoyé avec 500k lignes
```

### Erreur Dépendances
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

## 📋 Scripts de Démarrage Automatique

### Windows (PowerShell)
```powershell
.\start.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x start.sh
./start.sh
```

## 🎯 Prochaines Étapes

1. **Tester l'API** : http://localhost:8000/docs
2. **Adapter le frontend** pour utiliser l'API
3. **Charger plus de données** si nécessaire
4. **Optimiser les performances** avec Redis
5. **Déployer en production**

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs dans la console
2. Testez chaque composant séparément
3. Consultez la documentation FastAPI : http://localhost:8000/docs 