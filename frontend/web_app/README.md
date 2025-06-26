# 🌐 Frontend Web - SoGood

## 📋 Description

Application web Flask pour visualiser et rechercher les produits nutritionnels de la base de données Cassandra.

## 🚀 Démarrage rapide

### Prérequis
- Python 3.10+
- Base de données Cassandra avec des produits chargés
- API Backend SoGood en cours d'exécution

### Installation
```bash
cd frontend/web_app
pip install -r requirements.txt
```

### Démarrage
```bash
python app.py
```

L'application sera accessible sur http://localhost:5000

## 🏗️ Architecture

### Structure des fichiers
```
frontend/web_app/
├── app.py              # Application Flask principale
├── templates/          # Templates HTML
│   ├── base.html       # Template de base
│   ├── index.html      # Page d'accueil
│   └── product.html    # Page de détail produit
├── static/             # Fichiers statiques
│   ├── css/           # Styles CSS
│   └── images/        # Images
└── requirements.txt    # Dépendances Python
```

### Fonctionnalités
- **Recherche de produits** : Recherche par nom, marque, catégorie
- **Affichage des détails** : Informations nutritionnelles complètes
- **Images des produits** : Affichage des photos des produits
- **Interface responsive** : Compatible mobile et desktop

## 🔗 Intégration API

### Configuration
L'application se connecte à l'API Backend SoGood sur `http://localhost:8000`

### Endpoints utilisés
- `GET /api/products/search` - Recherche de produits
- `GET /api/products/{code}` - Détails d'un produit
- `GET /api/products` - Liste des produits

### Exemple d'utilisation
```python
import requests

# Recherche de produits
response = requests.get("http://localhost:8000/api/products/search", 
                       params={"q": "nutella"})
products = response.json()

# Détails d'un produit
response = requests.get("http://localhost:8000/api/products/3017620422003")
product = response.json()
```

## 🎨 Interface utilisateur

### Page d'accueil
- Barre de recherche
- Liste des produits récents
- Statistiques nutritionnelles

### Page de recherche
- Résultats de recherche
- Filtres par catégorie
- Pagination

### Page produit
- Informations détaillées
- Valeurs nutritionnelles
- Images du produit
- Grade Nutri-Score

## 🔧 Configuration

### Variables d'environnement
```bash
# URL de l'API Backend
API_BASE_URL=http://localhost:8000

# Port du serveur Flask
FLASK_PORT=5000

# Mode debug
FLASK_DEBUG=True
```

### Personnalisation
- Modifier `templates/` pour changer l'apparence
- Ajouter des filtres dans `app.py`
- Personnaliser les styles dans `static/css/`

## 🧪 Tests

### Test manuel
1. Démarrer l'API Backend
2. Démarrer le frontend
3. Ouvrir http://localhost:5000
4. Tester la recherche et l'affichage

### Test automatisé
```bash
# Tests unitaires (à implémenter)
python -m pytest tests/
```

## 🐛 Dépannage

### Erreur de connexion API
- Vérifier que l'API Backend est démarrée
- Vérifier l'URL dans la configuration
- Consulter les logs de l'API

### Erreur d'affichage
- Vérifier les templates HTML
- Consulter la console du navigateur
- Vérifier les fichiers statiques

### Erreur de données
- Vérifier que Cassandra contient des données
- Tester les endpoints API directement
- Vérifier le format des données

## 📈 Améliorations futures

- [ ] Interface d'administration
- [ ] Graphiques nutritionnels
- [ ] Comparaison de produits
- [ ] Système de favoris
- [ ] Export de données
- [ ] Mode sombre/clair
- [ ] Notifications push
- [ ] PWA (Progressive Web App)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Implémenter les changements
4. Tester localement
5. Soumettre une pull request

## 📞 Support

Pour toute question ou problème :
- Consulter la documentation
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement
