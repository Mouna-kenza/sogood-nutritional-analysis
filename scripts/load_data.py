import pandas as pd
import logging
from backend.database import setup_cassandra_connection, create_tables
from backend.models.product import Product
from backend.services.nutriscore_service import NutriscoreService
from backend.config import settings
import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Colonnes essentielles pour SoGood
ESSENTIAL_COLUMNS = [
    'code', 'product_name', 'brands', 'categories', 'countries',
    'energy_100g', 'fat_100g', 'saturated_fat_100g', 'carbohydrates_100g',
    'sugars_100g', 'fiber_100g', 'proteins_100g', 'salt_100g', 'sodium_100g',
    'nutriscore_grade', 'nutriscore_score', 'nova_group',
    'ingredients_text', 'allergens', 'additives_tags',
    'nutrition_grade_fr', 'completeness'
]

CSV_FILE_PATH = "notebooks/sogood_final_20250625_2235.csv"  # Fichier final nettoyé

class DataLoader:
    def __init__(self):
        self.nutriscore_service = NutriscoreService()
        self.processed_count = 0
        self.error_count = 0
    
    def clean_numeric_value(self, value) -> Optional[float]:
        """Nettoie et convertit les valeurs numériques"""
        if pd.isna(value) or value == '' or value == 'nan':
            return None
        try:
            # Supprimer les caractères non numériques sauf . et -
            if isinstance(value, str):
                value = value.replace(',', '.').strip()
                # Garder seulement les chiffres, points et tirets
                value = ''.join(c for c in value if c.isdigit() or c in '.-')
            return float(value) if value else None
        except (ValueError, TypeError):
            return None
    
    def clean_string_value(self, value, max_length: int = None) -> Optional[str]:
        """Nettoie les valeurs texte"""
        if pd.isna(value) or value == '':
            return None
        value = str(value).strip()
        if max_length and len(value) > max_length:
            value = value[:max_length]
        return value if value else None
    
    def calculate_completeness(self, row_data: Dict) -> float:
        """Calcule le pourcentage de complétude des données nutritionnelles"""
        nutrition_fields = [
            'energy_100g', 'fat_100g', 'carbohydrates_100g', 'sugars_100g',
            'fiber_100g', 'proteins_100g', 'salt_100g'
        ]
        
        filled_fields = sum(1 for field in nutrition_fields if row_data.get(field) is not None)
        return (filled_fields / len(nutrition_fields)) * 100
    
    def process_row(self, row) -> Optional[Dict]:
        """Traite une ligne du CSV et retourne un dictionnaire de données produit"""
        try:
            # Code produit (obligatoire)
            code = self.clean_string_value(row.get('code'), 50)
            if not code:
                return None
            
            # Données de base
            product_data = {
                'code': code,
                'product_name': self.clean_string_value(row.get('product_name'), 500),
                'brands': self.clean_string_value(row.get('brands'), 200),
                'categories': self.clean_string_value(row.get('categories'), 200),
                'countries': self.clean_string_value(row.get('countries'), 200),
                'ingredients_text': self.clean_string_value(row.get('ingredients_text'), 1000),
                'allergens': self.clean_string_value(row.get('allergens_tags'), 500),
                'additives': self.clean_string_value(row.get('additives_tags'), 500)
            }
            
            # Données nutritionnelles
            nutrition_data = {
                'energy_100g': self.clean_numeric_value(row.get('energy_100g')),
                'energy_kcal_100g': self.clean_numeric_value(row.get('energy-kcal_100g')),
                'fat_100g': self.clean_numeric_value(row.get('fat_100g')),
                'saturated_fat_100g': self.clean_numeric_value(row.get('saturated-fat_100g')),
                'carbohydrates_100g': self.clean_numeric_value(row.get('carbohydrates_100g')),
                'sugars_100g': self.clean_numeric_value(row.get('sugars_100g')),
                'fiber_100g': self.clean_numeric_value(row.get('fiber_100g')),
                'proteins_100g': self.clean_numeric_value(row.get('proteins_100g')),
                'salt_100g': self.clean_numeric_value(row.get('salt_100g')),
                'sodium_100g': self.clean_numeric_value(row.get('sodium_100g'))
            }
            
            # Scores
            nutriscore_grade = self.clean_string_value(row.get('nutriscore_grade'), 1)
            if nutriscore_grade:
                nutriscore_grade = nutriscore_grade.upper()
                if nutriscore_grade not in ['A', 'B', 'C', 'D', 'E']:
                    nutriscore_grade = 'N/A'
            else:
                nutriscore_grade = 'N/A'  # Valeur par défaut pour les produits sans Nutri-Score
            
            nova_group = self.clean_numeric_value(row.get('nova_group'))
            if nova_group and not (1 <= nova_group <= 4):
                nova_group = None
            
            # Calcul du Nutri-Score si manquant et données suffisantes
            nutriscore_score = self.clean_numeric_value(row.get('nutriscore_score'))
            if nutriscore_grade == 'N/A' and nutrition_data['energy_100g'] and nutrition_data['fat_100g']:
                try:
                    calculated = self.nutriscore_service.calculate_nutriscore(
                        energy_100g=nutrition_data['energy_100g'],
                        fat_100g=nutrition_data['fat_100g'],
                        saturated_fat_100g=nutrition_data['saturated_fat_100g'] or 0,
                        carbohydrates_100g=nutrition_data['carbohydrates_100g'] or 0,
                        sugars_100g=nutrition_data['sugars_100g'] or 0,
                        fiber_100g=nutrition_data['fiber_100g'],
                        proteins_100g=nutrition_data['proteins_100g'],
                        salt_100g=nutrition_data['salt_100g'],
                        sodium_100g=nutrition_data['sodium_100g']
                    )
                    nutriscore_grade = calculated['nutriscore_grade']
                    nutriscore_score = calculated['nutriscore_score']
                except Exception as e:
                    logger.warning(f"Erreur calcul Nutri-Score pour {code}: {e}")
                    # Garder 'N/A' si le calcul échoue
            
            # Complétude
            completeness = self.calculate_completeness(nutrition_data)
            
            # Données complètes pour Cassandra
            complete_data = {
                **product_data,
                **nutrition_data,
                'nutriscore_grade': nutriscore_grade,
                'nutriscore_score': int(nutriscore_score) if nutriscore_score else None,
                'nova_group': int(nova_group) if nova_group else None,
                'completeness': completeness,
                'created_at': datetime.utcnow()
            }
            
            # Log de debug pour les premiers produits
            if self.processed_count <= 5:
                logger.info(f"✅ Produit créé: {code} - {product_data.get('product_name', 'N/A')}")
            
            return complete_data
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement ligne {self.processed_count}: {e}")
            # Log de debug pour les premières erreurs
            if self.error_count <= 5:
                logger.error(f"   Détails ligne: {dict(row)}")
            return None
    
    def load_data(self, batch_size: int = 1000, max_rows: Optional[int] = None):
        """Charge les données du CSV en base"""
        logger.info(f"🚀 Début du chargement de {CSV_FILE_PATH}")
        
        # Créer les tables
        create_tables()
        
        # Lire le CSV par chunks pour gérer la mémoire
        chunk_size = 1000
        total_imported = 0
        
        try:
            # Lire le CSV avec les colonnes essentielles uniquement
            csv_columns = None
            df_test = pd.read_csv(CSV_FILE_PATH, sep=',', nrows=0)
            available_columns = df_test.columns.tolist()
            csv_columns = [col for col in ESSENTIAL_COLUMNS if col in available_columns]
            
            logger.info(f"📊 Colonnes disponibles: {len(csv_columns)}/{len(ESSENTIAL_COLUMNS)}")
            
            # Correction: usecols=None si csv_columns vide, nrows passé seulement si défini
            read_csv_kwargs = {
                'filepath_or_buffer': CSV_FILE_PATH,
                'sep': ',',
                'chunksize': chunk_size,
                'low_memory': False,
                'encoding': 'utf-8'
            }
            if csv_columns:
                read_csv_kwargs['usecols'] = csv_columns
            if max_rows is not None:
                read_csv_kwargs['nrows'] = max_rows

            for i, chunk in enumerate(pd.read_csv(**read_csv_kwargs)):
                if i == 0:
                    logger.info(f"Colonnes détectées: {chunk.columns.tolist()}")
                    logger.info(f"Premières lignes:\n{chunk.head()}")
                chunk_count = 0
                logger.info(f"📦 Traitement du chunk {total_imported + chunk_count} ({len(chunk)} lignes)")
                
                # Traiter le chunk
                products_batch = []
                
                for idx, row in chunk.iterrows():
                    self.processed_count += 1
                    
                    product = self.process_row(row)
                    if product:
                        products_batch.append(product)
                    else:
                        self.error_count += 1
                    
                    if self.processed_count % 5000 == 0:
                        logger.info(f"⏳ Traité {self.processed_count} lignes...")
                
                # Insérer en base par batch
                if products_batch:
                    self.insert_batch(products_batch)
                    logger.info(f"✅ Chunk {total_imported + chunk_count} inséré ({len(products_batch)} produits)")
                
                total_imported += len(products_batch)
        
        except Exception as e:
            logger.error(f"❌ Erreur lecture CSV: {e}")
            raise
        
        logger.info(f"🎉 Chargement terminé!")
        logger.info(f"📈 Statistiques:")
        logger.info(f"   - Lignes traitées: {self.processed_count}")
        logger.info(f"   - Erreurs: {self.error_count}")
        if self.processed_count > 0:
            logger.info(f"   - Taux de succès: {((self.processed_count - self.error_count) / self.processed_count * 100):.1f}%")
        else:
            logger.info("   - Taux de succès: 0% (aucune ligne traitée)")
    
    def insert_batch(self, products: list):
        """Insère un batch de produits en base en ignorant les doublons de code"""
        try:
            # Dédupliquer au niveau du batch (garder le premier de chaque code)
            seen_codes = set()
            unique_products = []
            for product in products:
                if product['code'] not in seen_codes:
                    seen_codes.add(product['code'])
                    unique_products.append(product)
            
            if not unique_products:
                return
            
            # Insérer les produits un par un avec gestion des erreurs
            inserted_count = 0
            for product_data in unique_products:
                try:
                    # Créer le produit avec cqlengine
                    Product.create(**product_data)
                    inserted_count += 1
                except Exception as e:
                    # Ignorer les erreurs de doublons
                    if "already exists" not in str(e).lower():
                        logger.warning(f"Erreur insertion produit {product_data.get('code')}: {e}")
                    continue
            
            logger.info(f"✅ {inserted_count} produits insérés dans ce batch")
            
        except Exception as e:
            logger.error(f"Erreur insertion batch: {e}")
            raise

def main():
    loader = DataLoader()
    loader.load_data(batch_size=2000)  # Charge tout le CSV, sans limite
    print(f"Total produits traités: {loader.processed_count}")
    print(f"Total erreurs: {loader.error_count}")

if __name__ == "__main__":
    main() 