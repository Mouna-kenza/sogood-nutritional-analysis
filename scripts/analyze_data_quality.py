#!/usr/bin/env python3
"""
Script pour analyser la qualité des données des produits
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, and_
from backend.database import engine
from backend.models.product import Product
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_data_quality():
    """Analyse la qualité des données des produits"""
    try:
        with engine.connect() as conn:
            # Statistiques générales
            total_products = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            
            # Produits avec données de base
            products_with_name = conn.execute(text("SELECT COUNT(*) FROM products WHERE product_name IS NOT NULL")).scalar()
            products_with_brand = conn.execute(text("SELECT COUNT(*) FROM products WHERE brands IS NOT NULL")).scalar()
            products_with_category = conn.execute(text("SELECT COUNT(*) FROM products WHERE categories IS NOT NULL")).scalar()
            
            # Produits avec scores nutritionnels
            products_with_nutriscore = conn.execute(text("SELECT COUNT(*) FROM products WHERE nutriscore_grade IS NOT NULL")).scalar()
            products_with_nova = conn.execute(text("SELECT COUNT(*) FROM products WHERE nova_group IS NOT NULL")).scalar()
            
            # Produits avec données nutritionnelles
            products_with_energy = conn.execute(text("SELECT COUNT(*) FROM products WHERE energy_kcal_100g IS NOT NULL")).scalar()
            products_with_fat = conn.execute(text("SELECT COUNT(*) FROM products WHERE fat_100g IS NOT NULL")).scalar()
            products_with_sugars = conn.execute(text("SELECT COUNT(*) FROM products WHERE sugars_100g IS NOT NULL")).scalar()
            products_with_salt = conn.execute(text("SELECT COUNT(*) FROM products WHERE salt_100g IS NOT NULL")).scalar()
            products_with_proteins = conn.execute(text("SELECT COUNT(*) FROM products WHERE proteins_100g IS NOT NULL")).scalar()
            
            # Produits avec données complètes (critères stricts)
            complete_products = conn.execute(text("""
                SELECT COUNT(*) FROM products 
                WHERE product_name IS NOT NULL 
                AND brands IS NOT NULL 
                AND nutriscore_grade IS NOT NULL 
                AND nova_group IS NOT NULL 
                AND energy_kcal_100g IS NOT NULL 
                AND fat_100g IS NOT NULL 
                AND sugars_100g IS NOT NULL 
                AND salt_100g IS NOT NULL 
                AND proteins_100g IS NOT NULL
                AND nutriscore_grade != 'N/A'
                AND nova_group > 0
                AND energy_kcal_100g > 0
            """)).scalar()
            
            # Afficher les résultats
            print("📊 Analyse de la Qualité des Données")
            print("=" * 50)
            print(f"Total de produits: {total_products}")
            print()
            print("📋 Données de base:")
            print(f"  - Nom du produit: {products_with_name} ({products_with_name/total_products*100:.1f}%)")
            print(f"  - Marque: {products_with_brand} ({products_with_brand/total_products*100:.1f}%)")
            print(f"  - Catégorie: {products_with_category} ({products_with_category/total_products*100:.1f}%)")
            print()
            print("🏆 Scores nutritionnels:")
            print(f"  - Nutri-Score: {products_with_nutriscore} ({products_with_nutriscore/total_products*100:.1f}%)")
            print(f"  - NOVA: {products_with_nova} ({products_with_nova/total_products*100:.1f}%)")
            print()
            print("📊 Données nutritionnelles:")
            print(f"  - Énergie: {products_with_energy} ({products_with_energy/total_products*100:.1f}%)")
            print(f"  - Lipides: {products_with_fat} ({products_with_fat/total_products*100:.1f}%)")
            print(f"  - Sucres: {products_with_sugars} ({products_with_sugars/total_products*100:.1f}%)")
            print(f"  - Sel: {products_with_salt} ({products_with_salt/total_products*100:.1f}%)")
            print(f"  - Protéines: {products_with_proteins} ({products_with_proteins/total_products*100:.1f}%)")
            print()
            print("✅ Produits avec données complètes:")
            print(f"  - Nombre: {complete_products} ({complete_products/total_products*100:.1f}%)")
            
            # Exemples de produits complets
            if complete_products > 0:
                print()
                print("🔍 Exemples de produits complets:")
                examples = conn.execute(text("""
                    SELECT id, product_name, brands, nutriscore_grade, nova_group, energy_kcal_100g
                    FROM products 
                    WHERE product_name IS NOT NULL 
                    AND brands IS NOT NULL 
                    AND nutriscore_grade IS NOT NULL 
                    AND nova_group IS NOT NULL 
                    AND energy_kcal_100g IS NOT NULL 
                    AND fat_100g IS NOT NULL 
                    AND sugars_100g IS NOT NULL 
                    AND salt_100g IS NOT NULL 
                    AND proteins_100g IS NOT NULL
                    AND nutriscore_grade != 'N/A'
                    AND nova_group > 0
                    AND energy_kcal_100g > 0
                    LIMIT 5
                """)).fetchall()
                
                for example in examples:
                    print(f"  - {example[1]} ({example[2]}) - Nutri-Score: {example[3]}, NOVA: {example[4]}")
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse: {e}")
        raise

def main():
    """Fonction principale"""
    print("🔍 Analyse de la qualité des données SoGood")
    print("=" * 50)
    
    try:
        analyze_data_quality()
        print()
        print("✅ Analyse terminée")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 