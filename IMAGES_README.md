# 🖼️ Images des Produits - SoGood

## 📋 Vue d'ensemble

L'application SoGood supporte maintenant l'affichage d'images pour les produits alimentaires. Les images proviennent d'OpenFoodFacts et sont affichées dans l'interface web.

## 🗄️ Structure de la Base de Données

### Nouvelles Colonnes Ajoutées

La table `products` a été étendue avec les colonnes suivantes :

```sql
ALTER TABLE products 
ADD COLUMN image_url VARCHAR(1000),           -- Image principale
ADD COLUMN image_front_url VARCHAR(1000),     -- Image avant du produit
ADD COLUMN image_ingredients_url VARCHAR(1000), -- Image des ingrédients
ADD COLUMN image_nutrition_url VARCHAR(1000);   -- Image nutritionnelle
```

### Types d'Images Supportés

1. **Image principale** (`image_url`) : Image générique du produit
2. **Image avant** (`image_front_url`) : Vue avant du packaging
3. **Image ingrédients** (`image_ingredients_url`) : Liste des ingrédients
4. **Image nutrition** (`image_nutrition_url`) : Tableau nutritionnel

## 🚀 Installation et Configuration

### 1. Mettre à jour la Base de Données

```bash
# Exécuter le script de mise à jour
python scripts/update_db_images.py
```

### 2. Redémarrer l'Application

```bash
# Redémarrer le backend
docker-compose restart backend

# Ou redémarrer manuellement
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Tester le Frontend

```bash
# Démarrer le frontend
python start_frontend.py
```

## 🎨 Affichage dans l'Interface

### Page d'Accueil (Recherche)

- **Cartes de produits** : Affichage de l'image principale
- **Placeholder** : Icône si aucune image disponible
- **Gestion d'erreurs** : Masquage automatique si image invalide

### Page de Détail Produit

- **Image principale** : Grande image en haut de la page
- **Images additionnelles** : Vignettes pour les autres vues
- **Galerie** : Affichage de toutes les images disponibles

## 🔧 Fonctionnalités Techniques

### Modèle Product

```python
class Product(Base):
    # ... autres champs ...
    
    # Images
    image_url = Column(String(1000))
    image_front_url = Column(String(1000))
    image_ingredients_url = Column(String(1000))
    image_nutrition_url = Column(String(1000))
    
    def get_best_image_url(self) -> str | None:
        """Retourne la meilleure URL d'image disponible"""
        if self.image_front_url:
            return self.image_front_url
        elif self.image_url:
            return self.image_url
        elif self.image_ingredients_url:
            return self.image_ingredients_url
        elif self.image_nutrition_url:
            return self.image_nutrition_url
        else:
            return None
```

### API Backend

#### Recherche de Produits
```json
{
  "id": "1",
  "name": "Nom du produit",
  "brand": "Marque",
  "image_url": "https://images.openfoodfacts.org/...",
  // ... autres champs
}
```

#### Détail Produit
```json
{
  "id": "1",
  "name": "Nom du produit",
  "images": {
    "main": "https://images.openfoodfacts.org/...",
    "front": "https://images.openfoodfacts.org/...",
    "ingredients": "https://images.openfoodfacts.org/...",
    "nutrition": "https://images.openfoodfacts.org/...",
    "best": "https://images.openfoodfacts.org/..."
  },
  // ... autres champs
}
```

## 🎯 Sources d'Images

### OpenFoodFacts

Les images proviennent principalement d'OpenFoodFacts avec le format d'URL :
```
https://images.openfoodfacts.org/images/products/{CODE}/{front|ingredients|nutrition}_{lang}.{size}.{format}
```

### Exemples d'URLs

- **Vue avant** : `https://images.openfoodfacts.org/images/products/301/762/042/2003/front_fr.147.400.jpg`
- **Ingrédients** : `https://images.openfoodfacts.org/images/products/301/762/042/2003/ingredients_fr.147.400.jpg`
- **Nutrition** : `https://images.openfoodfacts.org/images/products/301/762/042/2003/nutrition_fr.147.400.jpg`

## 🛠️ Personnalisation

### Styles CSS

Les images utilisent les classes CSS suivantes :

```css
.product-image {
    height: 200px;
    object-fit: contain;
    background-color: #f8f9fa;
    padding: 10px;
}

.product-image-placeholder {
    height: 200px;
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
}

.main-product-image img {
    max-height: 300px;
    width: 100%;
    object-fit: contain;
}
```

### Gestion d'Erreurs

- **Images manquantes** : Affichage d'un placeholder
- **URLs invalides** : Masquage automatique avec `onerror="this.style.display='none'"`
- **Chargement** : Optimisation avec `object-fit: contain`

## 📊 Statistiques

### Métriques d'Images

- **Produits avec images** : Pourcentage de produits ayant au moins une image
- **Qualité des images** : Distribution par type d'image
- **Complétude** : Indicateur de la richesse visuelle de la base

### Requêtes Utiles

```sql
-- Produits avec images
SELECT COUNT(*) FROM products WHERE image_url IS NOT NULL;

-- Distribution par type d'image
SELECT 
    COUNT(image_url) as main_images,
    COUNT(image_front_url) as front_images,
    COUNT(image_ingredients_url) as ingredients_images,
    COUNT(image_nutrition_url) as nutrition_images
FROM products;
```

## 🔮 Améliorations Futures

### Fonctionnalités Prévues

1. **Upload d'images** : Permettre aux utilisateurs d'ajouter des images
2. **Galerie interactive** : Zoom et navigation entre images
3. **Cache d'images** : Optimisation des performances
4. **Images alternatives** : Fallback vers d'autres sources
5. **OCR sur images** : Extraction automatique d'informations

### Intégrations Possibles

- **APIs d'images** : Intégration avec d'autres sources
- **CDN** : Optimisation de la distribution
- **Compression** : Réduction de la taille des images
- **Responsive** : Adaptation mobile avancée

## 🚨 Dépannage

### Problèmes Courants

1. **Images ne s'affichent pas**
   - Vérifier les URLs dans la base de données
   - Contrôler la connectivité internet
   - Vérifier les permissions CORS

2. **Images cassées**
   - URLs OpenFoodFacts peuvent changer
   - Implémenter un système de fallback
   - Utiliser des images par défaut

3. **Performance lente**
   - Optimiser la taille des images
   - Implémenter un cache
   - Utiliser un CDN

### Logs Utiles

```bash
# Vérifier les colonnes d'images
python scripts/update_db_images.py

# Tester une URL d'image
curl -I "https://images.openfoodfacts.org/images/products/301/762/042/2003/front_fr.147.400.jpg"
```

## 📝 Notes

- Les images sont hébergées par OpenFoodFacts
- Pas de stockage local des images pour l'instant
- Gestion gracieuse des erreurs d'affichage
- Interface responsive pour tous les appareils
- Optimisation pour les performances web 