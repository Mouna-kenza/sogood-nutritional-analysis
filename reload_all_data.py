#!/usr/bin/env python3
"""
Script pour recharger TOUS les produits du CSV sans filtres restrictifs
"""

import pandas as pd
import logging
from backend.database import setup_cassandra_connection, create_tables
from backend.models.product import Product
from datetime import datetime
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSV_FILE_PATH = "notebooks/sogood_final_20250625_2235.csv"

class FullDataLoader:
    def __init__(self):
        self.processed_count = 0
        self.inserted_count = 0
        self.error_count = 0
    
    def clean_value(self, value, max_length=None):
        """Nettoie une valeur de manière permissive"""
        if pd.isna(value) or value == '' or value == 'nan':
            return None
        
        value = str(value).strip()
        if max_length and len(value) > max_length:
            value = value[:max_length]
        return value if value else None
    
    def clean_numeric(self, value):
        """Nettoie une valeur numérique de manière permissive"""
        if pd.isna(value) or value == '' or value == 'nan':
            return None
        
        try:
            if isinstance(value, str):
                value = value.replace(',', '.').strip()
                value = ''.join(c for c in value if c.isdigit() or c in '.-')
            return float(value) if value else None
        except:
            return None
    
    def process_row(self, row):
        """Traite une ligne avec des filtres minimaux"""
        try:
            # Code produit (obligatoire)
            code = self.clean_value(row.get('code'), 50)
            if not code:
                return None
            
            # Nom du produit (obligatoire)
            product_name = self.clean_value(row.get('product_name'), 500)
            if not product_name:
                return None
            
            # Données de base
            product_data = {
                'code': code,
                'product_name': product_name,
                'brands': self.clean_value(row.get('brands'), 200),
                'categories': self.clean_value(row.get('categories'), 200),
                'countries': self.clean_value(row.get('countries'), 200),
                'ingredients_text': self.clean_value(row.get('ingredients_text'), 1000),
                'allergens': self.clean_value(row.get('allergens'), 500),
                'additives': self.clean_value(row.get('additives'), 500)
            }
            
            # Données nutritionnelles (toutes optionnelles)
            nutrition_data = {
                'energy_100g': self.clean_numeric(row.get('energy_100g')),
                'energy_kcal_100g': self.clean_numeric(row.get('energy-kcal_100g')),
                'fat_100g': self.clean_numeric(row.get('fat_100g')),
                'saturated_fat_100g': self.clean_numeric(row.get('saturated-fat_100g')),
                'carbohydrates_100g': self.clean_numeric(row.get('carbohydrates_100g')),
                'sugars_100g': self.clean_numeric(row.get('sugars_100g')),
                'fiber_100g': self.clean_numeric(row.get('fiber_100g')),
                'proteins_100g': self.clean_numeric(row.get('proteins_100g')),
                'salt_100g': self.clean_numeric(row.get('salt_100g')),
                'sodium_100g': self.clean_numeric(row.get('sodium_100g'))
            }
            
            # Nutri-Score (optionnel)
            nutriscore_grade = self.clean_value(row.get('nutriscore_grade'), 1)
            if nutriscore_grade:
                nutriscore_grade = nutriscore_grade.upper()
                if nutriscore_grade not in ['A', 'B', 'C', 'D', 'E']:
                    nutriscore_grade = 'N/A'
            else:
                nutriscore_grade = 'N/A'
            
            # NOVA Group (optionnel)
            nova_group = self.clean_numeric(row.get('nova_group'))
            if nova_group and not (1 <= nova_group <= 4):
                nova_group = None
            
            # Nutri-Score Score (optionnel)
            nutriscore_score = self.clean_numeric(row.get('nutriscore_score'))
            
            # Complétude (calculée)
            nutrition_fields = ['energy_100g', 'fat_100g', 'carbohydrates_100g', 'sugars_100g', 'fiber_100g', 'proteins_100g', 'salt_100g']
            filled_fields = sum(1 for field in nutrition_fields if nutrition_data.get(field) is not None)
            completeness = (filled_fields / len(nutrition_fields)) * 100
            
            # Données complètes
            complete_data = {
                **product_data,
                **nutrition_data,
                'nutriscore_grade': nutriscore_grade,
                'nutriscore_score': int(nutriscore_score) if nutriscore_score else None,
                'nova_group': int(nova_group) if nova_group else None,
                'completeness': completeness,
                'created_at': datetime.utcnow()
            }
            
            return complete_data
            
        except Exception as e:
            logger.error(f"Erreur traitement ligne {self.processed_count}: {e}")
            return None
    
    def load_all_data(self):
        """Charge TOUS les produits du CSV"""
        logger.info(f"🚀 Début du chargement complet de {CSV_FILE_PATH}")
        
        # Créer les tables
        create_tables()
        
        # Vider la table existante
        logger.info("🗑️ Vidage de la table existante...")
        try:
            Product.objects.all().delete()
            logger.info("✅ Table vidée")
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors du vidage: {e}")
        
        try:
            # Lire le CSV
            logger.info("📖 Lecture du CSV...")
            df = pd.read_csv(CSV_FILE_PATH, low_memory=False)
            logger.info(f"📊 CSV lu: {len(df):,} lignes")
            
            # Traiter par chunks
            chunk_size = 1000
            total_chunks = (len(df) + chunk_size - 1) // chunk_size
            
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i+chunk_size]
                chunk_num = i // chunk_size + 1
                
                logger.info(f"📦 Traitement chunk {chunk_num}/{total_chunks} ({len(chunk)} lignes)")
                
                products_batch = []
                
                for idx, row in chunk.iterrows():
                    self.processed_count += 1
                    
                    product = self.process_row(row)
                    if product:
                        products_batch.append(product)
                    else:
                        self.error_count += 1
                    
                    if self.processed_count % 10000 == 0:
                        logger.info(f"⏳ Traité {self.processed_count:,} lignes...")
                
                # Insérer le batch
                if products_batch:
                    self.insert_batch(products_batch)
                    logger.info(f"✅ Chunk {chunk_num} inséré ({len(products_batch)} produits)")
                
                # Afficher le progrès
                progress = (chunk_num / total_chunks) * 100
                logger.info(f"📈 Progrès: {progress:.1f}% ({self.inserted_count:,} produits insérés)")
        
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement: {e}")
            raise
        
        logger.info(f"🎉 Chargement terminé!")
        logger.info(f"📈 Statistiques finales:")
        logger.info(f"   - Lignes traitées: {self.processed_count:,}")
        logger.info(f"   - Produits insérés: {self.inserted_count:,}")
        logger.info(f"   - Erreurs: {self.error_count:,}")
        if self.processed_count > 0:
            success_rate = ((self.processed_count - self.error_count) / self.processed_count) * 100
            logger.info(f"   - Taux de succès: {success_rate:.1f}%")
    
    def insert_batch(self, products):
        """Insère un batch de produits"""
        try:
            inserted_count = 0
            for product_data in products:
                try:
                    Product.create(**product_data)
                    inserted_count += 1
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        logger.warning(f"Erreur insertion produit {product_data.get('code')}: {e}")
                    continue
            
            self.inserted_count += inserted_count
            
        except Exception as e:
            logger.error(f"Erreur insertion batch: {e}")
            raise

def main():
    """Fonction principale"""
    print("🚀 RECHARGEMENT COMPLET DES DONNÉES")
    print("=" * 50)
    print("⚠️  ATTENTION: Ce script va vider la base et recharger TOUS les produits!")
    print("   Cela peut prendre plusieurs minutes...")
    
    response = input("\nContinuer? (y/N): ")
    if response.lower() != 'y':
        print("❌ Annulé")
        return
    
    loader = FullDataLoader()
    loader.load_all_data()

if __name__ == "__main__":
    main() 