from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.usertype import UserType
from datetime import datetime
import logging
from decimal import Decimal
from typing import Optional

class Product(Model):
    """
    Modèle Cassandra pour les produits alimentaires
    """
    __keyspace__ = 'sogood'
    __table_name__ = 'products'
    
    # Clé primaire (partition key)
    code = columns.Text(primary_key=True, partition_key=True)
    
    # Clustering keys pour l'ordre et les requêtes
    created_at = columns.DateTime(primary_key=True, clustering_order="DESC")
    nutriscore_grade = columns.Text(primary_key=True, clustering_order="ASC")
    
    # Informations de base
    product_name = columns.Text()
    brands = columns.Text()
    categories = columns.Text()
    countries = columns.Text()
    
    # Images
    image_url = columns.Text()
    image_front_url = columns.Text()
    image_ingredients_url = columns.Text()
    image_nutrition_url = columns.Text()
    
    # Valeurs nutritionnelles pour 100g
    energy_100g = columns.Decimal()
    energy_kcal_100g = columns.Decimal()
    fat_100g = columns.Decimal()
    saturated_fat_100g = columns.Decimal()
    carbohydrates_100g = columns.Decimal()
    sugars_100g = columns.Decimal()
    fiber_100g = columns.Decimal()
    proteins_100g = columns.Decimal()
    salt_100g = columns.Decimal()
    sodium_100g = columns.Decimal()
    
    # Scores nutritionnels
    nutriscore_score = columns.Integer()
    nova_group = columns.Integer(required=False)
    
    # Informations supplémentaires
    ingredients_text = columns.Text()
    allergens = columns.Text()
    additives = columns.Text()
    
    # Qualité des données
    completeness = columns.Decimal()
    
    # Métadonnées
    updated_at = columns.DateTime(default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product(code={self.code}, name={self.product_name}, nutriscore={self.nutriscore_grade})>"
    
    @property
    def nutrition_available(self) -> bool:
        """Vérifie si les données nutritionnelles sont disponibles"""
        return all([
            self.energy_100g is not None,
            self.fat_100g is not None,
            self.proteins_100g is not None
        ])
    
    @property
    def has_images(self) -> bool:
        """Vérifie si le produit a des images disponibles"""
        return any([
            self.image_url,
            self.image_front_url,
            self.image_ingredients_url,
            self.image_nutrition_url
        ])
    
    def get_best_image_url(self) -> Optional[str]:
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
    
    def to_dict(self) -> dict:
        """Convertit le modèle en dictionnaire"""
        return {
            'code': self.code,
            'product_name': self.product_name,
            'brands': self.brands,
            'categories': self.categories,
            'countries': self.countries,
            'images': {
                'main': self.image_url,
                'front': self.image_front_url,
                'ingredients': self.image_ingredients_url,
                'nutrition': self.image_nutrition_url,
                'best': self.get_best_image_url()
            },
            'nutrition': {
                'energy_100g': float(self.energy_100g) if self.energy_100g else None,
                'energy_kcal_100g': float(self.energy_kcal_100g) if self.energy_kcal_100g else None,
                'fat_100g': float(self.fat_100g) if self.fat_100g else None,
                'saturated_fat_100g': float(self.saturated_fat_100g) if self.saturated_fat_100g else None,
                'carbohydrates_100g': float(self.carbohydrates_100g) if self.carbohydrates_100g else None,
                'sugars_100g': float(self.sugars_100g) if self.sugars_100g else None,
                'fiber_100g': float(self.fiber_100g) if self.fiber_100g else None,
                'proteins_100g': float(self.proteins_100g) if self.proteins_100g else None,
                'salt_100g': float(self.salt_100g) if self.salt_100g else None,
                'sodium_100g': float(self.sodium_100g) if self.sodium_100g else None,
            },
            'scores': {
                'nutriscore_grade': self.nutriscore_grade,
                'nutriscore_score': self.nutriscore_score,
                'nova_group': self.nova_group,
            },
            'ingredients_text': self.ingredients_text,
            'allergens': self.allergens,
            'additives': self.additives,
            'completeness': float(self.completeness) if self.completeness else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def create_from_dict(cls, data: dict) -> 'Product':
        """Crée un produit à partir d'un dictionnaire"""
        # Convertir les valeurs décimales
        nutrition_fields = [
            'energy_100g', 'energy_kcal_100g', 'fat_100g', 'saturated_fat_100g',
            'carbohydrates_100g', 'sugars_100g', 'fiber_100g', 'proteins_100g',
            'salt_100g', 'sodium_100g', 'completeness'
        ]
        
        for field in nutrition_fields:
            if field in data and data[field] is not None:
                data[field] = Decimal(str(data[field]))
        
        # Gérer les données imbriquées
        if 'nutrition' in data:
            for key, value in data['nutrition'].items():
                if value is not None:
                    data[key] = Decimal(str(value))
            del data['nutrition']
        
        if 'scores' in data:
            for key, value in data['scores'].items():
                data[key] = value
            del data['scores']
        
        if 'images' in data:
            for key, value in data['images'].items():
                if key == 'main':
                    data['image_url'] = value
                elif key == 'front':
                    data['image_front_url'] = value
                elif key == 'ingredients':
                    data['image_ingredients_url'] = value
                elif key == 'nutrition':
                    data['image_nutrition_url'] = value
            del data['images']
        
        # Créer le produit
        return cls.create(**data) 