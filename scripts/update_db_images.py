#!/usr/bin/env python3
"""
Script pour ajouter les colonnes d'images à la base de données
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.database import get_db, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_image_columns():
    """Ajoute les colonnes d'images à la table products"""
    try:
        with engine.connect() as conn:
            # Vérifier si les colonnes existent déjà
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'products' 
                AND column_name IN ('image_url', 'image_front_url', 'image_ingredients_url', 'image_nutrition_url')
            """))
            existing_columns = [row[0] for row in result]
            
            if not existing_columns:
                logger.info("Ajout des colonnes d'images...")
                
                # Ajouter les colonnes d'images
                conn.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN image_url VARCHAR(1000),
                    ADD COLUMN image_front_url VARCHAR(1000),
                    ADD COLUMN image_ingredients_url VARCHAR(1000),
                    ADD COLUMN image_nutrition_url VARCHAR(1000)
                """))
                
                conn.commit()
                logger.info("✅ Colonnes d'images ajoutées avec succès")
            else:
                logger.info(f"⚠️ Colonnes d'images déjà présentes: {existing_columns}")
                
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ajout des colonnes: {e}")
        raise

def update_sample_images():
    """Met à jour quelques produits avec des URLs d'images d'exemple"""
    try:
        with engine.connect() as conn:
            # Exemple d'URLs d'images OpenFoodFacts
            sample_images = [
                {
                    'code': '3017620422003',
                    'image_url': 'https://images.openfoodfacts.org/images/products/301/762/042/2003/front_fr.147.400.jpg',
                    'image_front_url': 'https://images.openfoodfacts.org/images/products/301/762/042/2003/front_fr.147.400.jpg',
                    'image_ingredients_url': 'https://images.openfoodfacts.org/images/products/301/762/042/2003/ingredients_fr.147.400.jpg',
                    'image_nutrition_url': 'https://images.openfoodfacts.org/images/products/301/762/042/2003/nutrition_fr.147.400.jpg'
                },
                {
                    'code': '3228857000902',
                    'image_url': 'https://images.openfoodfacts.org/images/products/322/885/700/0902/front_fr.147.400.jpg',
                    'image_front_url': 'https://images.openfoodfacts.org/images/products/322/885/700/0902/front_fr.147.400.jpg',
                    'image_ingredients_url': 'https://images.openfoodfacts.org/images/products/322/885/700/0902/ingredients_fr.147.400.jpg',
                    'image_nutrition_url': 'https://images.openfoodfacts.org/images/products/322/885/700/0902/nutrition_fr.147.400.jpg'
                }
            ]
            
            for sample in sample_images:
                conn.execute(text("""
                    UPDATE products 
                    SET image_url = :image_url,
                        image_front_url = :image_front_url,
                        image_ingredients_url = :image_ingredients_url,
                        image_nutrition_url = :image_nutrition_url
                    WHERE code = :code
                """), sample)
            
            conn.commit()
            logger.info("✅ Images d'exemple ajoutées")
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ajout des images d'exemple: {e}")

def main():
    """Fonction principale"""
    print("🖼️ Mise à jour de la base de données pour les images")
    print("=" * 50)
    
    try:
        # Ajouter les colonnes d'images
        add_image_columns()
        
        # Ajouter quelques images d'exemple
        update_sample_images()
        
        print("✅ Mise à jour terminée avec succès")
        print("💡 Les produits peuvent maintenant afficher des images")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 