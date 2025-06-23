# Database & Infrastructure - Giscard 🔧

## 🎯 Tes Responsabilités
Setup infrastructure backend complète

## ❓ À Décider Ensemble
- **BDD** : PostgreSQL / MySQL / SQLite ?
- **Hébergement** : Local / Cloud ?
- **APIs** : Flask / FastAPI ?

## 🗃️ Tables à Créer
```sql
-- Produits de base
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE,
    name VARCHAR(500),
    brand VARCHAR(200),
    category VARCHAR(200),
    created_at TIMESTAMP
);

-- Valeurs nutritionnelles  
CREATE TABLE nutritional_values (
    product_id INT REFERENCES products(id),
    energy_100g FLOAT,
    fat_100g FLOAT,
    sugar_100g FLOAT,
    salt_100g FLOAT,
    fiber_100g FLOAT,
    proteins_100g FLOAT
);

-- Scores calculés
CREATE TABLE quality_scores (
    product_id INT REFERENCES products(id),
    nutri_score CHAR(1), -- A, B, C, D, E
    nova_score INT,      -- 1, 2, 3, 4
    controversies TEXT[], -- Array des problèmes
    calculated_at TIMESTAMP
);
