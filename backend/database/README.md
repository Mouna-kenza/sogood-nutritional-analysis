# Database & Infrastructure - Giscard 🔧

## 🎯 Tes Responsabilités
Setup infrastructure backend complète avec Cassandra

## ✅ Décision Finale
- **BDD** : Cassandra ✅
- **Hébergement** : Docker avec Cassandra 4.1
- **APIs** : FastAPI avec cqlengine

## 🗃️ Tables à Créer
```cql
-- Keyspace
CREATE KEYSPACE IF NOT EXISTS sogood
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

-- Table des produits
CREATE TABLE sogood.products (
    code text,
    created_at timestamp,
    nutriscore_grade text,
    product_name text,
    brands text,
    categories text,
    countries text,
    image_url text,
    image_front_url text,
    image_ingredients_url text,
    image_nutrition_url text,
    energy_100g decimal,
    energy_kcal_100g decimal,
    fat_100g decimal,
    saturated_fat_100g decimal,
    carbohydrates_100g decimal,
    sugars_100g decimal,
    fiber_100g decimal,
    proteins_100g decimal,
    salt_100g decimal,
    sodium_100g decimal,
    nutriscore_score int,
    nova_group int,
    ingredients_text text,
    allergens text,
    additives text,
    completeness decimal,
    updated_at timestamp,
    PRIMARY KEY (code, created_at, nutriscore_grade)
) WITH CLUSTERING ORDER BY (created_at DESC, nutriscore_grade ASC);
```

## 🔧 Configuration
- **Hosts**: cassandra (Docker) / localhost (dev)
- **Port**: 9042
- **Keyspace**: sogood
- **Datacenter**: datacenter1

## 📊 Avantages Cassandra
- **Scalabilité horizontale** : Distribution sur plusieurs nœuds
- **Haute disponibilité** : Réplication automatique
- **Performance** : Optimisé pour les lectures/écritures
- **Flexibilité** : Schéma flexible pour les données nutritionnelles