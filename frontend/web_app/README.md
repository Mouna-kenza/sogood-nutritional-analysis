# Frontend SoGood - Interface Web Flask

## 🎯 Description

Interface web Flask pour l'application SoGood d'analyse nutritionnelle. Le frontend se connecte à l'API backend FastAPI pour afficher les produits de la base de données OpenFoodFacts.

## 🚀 Démarrage Rapide

### Prérequis
- Backend FastAPI démarré sur `http://localhost:8000`
- Base de données PostgreSQL avec des produits chargés
- Python 3.8+

### Installation et démarrage

1. **Vérifier que le backend est démarré :**
```bash
# Option 1: Avec Docker
docker-compose up backend

# Option 2: Directement
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Démarrer le frontend :**
```bash
# Depuis la racine du projet
python start_frontend.py

# Ou directement
cd frontend/web_app
python app.py
```

3. **Accéder à l'interface :**
- URL: http://localhost:5000
- L'interface se connecte automatiquement à l'API backend

## 🔧 Fonctionnalités

### Page d'accueil (`/`)
- **Recherche de produits** : Recherche par nom, marque ou catégorie
- **Filtres** : Par catégorie et Nutri-Score
- **Affichage des résultats** : Cartes avec informations nutritionnelles
- **Navigation** : Vers les pages de détail des produits

### Page produit (`/product/<id>`)
- **Informations détaillées** : Nom, marque, catégorie, code
- **Scores nutritionnels** : Nutri-Score et NOVA
- **Valeurs nutritionnelles** : Tableau complet (énergie, lipides, glucides, etc.)
- **Alertes** : Controverses détectées automatiquement
- **Informations complémentaires** : Ingrédients, allergènes, additifs
- **Qualité des données** : Indicateur de complétude

## 📊 Structure des Données

Le frontend utilise la structure de données suivante du backend :

### Produit (recherche)
```json
{
  "id": "1",
  "name": "Nom du produit",
  "brand": "Marque",
  "category": "Catégorie",
  "nutri_score": "A",
  "nova_score": 1,
  "energy_100g": 150.0,
  "controversies": ["Très riche en sucre"]
}
```

### Produit (détail)
```json
{
  "id": "1",
  "code": "123456789",
  "name": "Nom du produit",
  "brand": "Marque",
  "category": "Catégorie",
  "nutri_score": "A",
  "nova_score": 1,
  "nutrition": {
    "energy_100g": 150.0,
    "fat_100g": 2.5,
    "saturated_fat_100g": 1.0,
    "carbohydrates_100g": 25.0,
    "sugars_100g": 5.0,
    "fiber_100g": 3.0,
    "proteins_100g": 8.0,
    "salt_100g": 0.5
  },
  "ingredients": "Liste des ingrédients...",
  "allergens": "Allergènes présents",
  "additives": "Additifs utilisés",
  "controversies": ["Très riche en sucre"],
  "completeness": 85.5
}
```

## 🎨 Interface Utilisateur

### Design
- **Bootstrap 5** : Framework CSS moderne
- **Font Awesome** : Icônes
- **Responsive** : Compatible mobile et desktop
- **Thème vert** : Couleurs cohérentes avec l'identité SoGood

### Composants
- **Navbar** : Navigation principale
- **Hero section** : En-tête avec titre
- **Cartes de produits** : Affichage des résultats
- **Tableaux nutritionnels** : Données détaillées
- **Badges et alertes** : Indicateurs visuels

## 🔗 Intégration API

### Routes utilisées
- `GET /api/v1/products/search` : Recherche de produits
- `GET /api/v1/products/{id}` : Détail d'un produit
- `GET /api/v1/products/stats/database` : Statistiques (optionnel)

### Gestion d'erreurs
- **Connexion API** : Messages d'erreur explicites
- **Produits non trouvés** : Affichage approprié
- **Données manquantes** : Valeurs par défaut

## 🛠️ Développement

### Structure des fichiers
```
frontend/web_app/
├── app.py              # Application Flask principale
├── templates/          # Templates Jinja2
│   ├── base.html      # Template de base
│   ├── index.html     # Page d'accueil
│   └── product.html   # Page produit
└── README.md          # Documentation
```

### Personnalisation
- **Styles CSS** : Modifier `base.html` ou ajouter des fichiers CSS
- **Templates** : Adapter les templates Jinja2
- **Logique** : Modifier `app.py` pour ajouter des fonctionnalités

## 📝 Notes

- Le frontend utilise les données de la base PostgreSQL via l'API backend
- L'ancien fichier CSV `frontend/power_bi/sogood_data.csv` a été supprimé
- Toutes les données proviennent maintenant de la base de données OpenFoodFacts
- L'interface est optimisée pour afficher les informations nutritionnelles de manière claire et accessible

## 🚨 Dépannage

### Problèmes courants

1. **Frontend ne se connecte pas au backend**
   - Vérifier que l'API backend est démarrée sur le port 8000
   - Contrôler les logs du backend pour les erreurs de connexion DB

2. **Aucun produit affiché**
   - Vérifier que la base de données contient des produits
   - Utiliser le script `scripts/load_data.py` pour charger des données

3. **Erreurs 500 sur les pages produit**
   - Vérifier la structure des données retournées par l'API
   - Contrôler les logs du backend pour les erreurs SQL

### Logs utiles
```bash
# Logs du backend
docker-compose logs backend

# Logs du frontend (dans le terminal de démarrage)
python start_frontend.py
```
