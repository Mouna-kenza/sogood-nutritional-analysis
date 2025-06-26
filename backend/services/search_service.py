"""
Service de recherche de produits pour Cassandra
"""
import logging
from typing import List, Optional
from backend.models.product import Product

logger = logging.getLogger(__name__)

class SearchService:
    """Service de recherche de produits"""
    
    def search_products(self, query: str, limit: int = 20) -> List[Product]:
        """
        Recherche de produits par texte
        """
        try:
            # Récupérer tous les produits et filtrer en mémoire
            all_products = list(Product.objects.all())
            
            # Filtrer par la requête
            query_lower = query.lower()
            filtered_products = []
            
            for product in all_products:
                if (query_lower in (product.product_name or '').lower() or
                    query_lower in (product.brands or '').lower() or
                    query_lower in (product.categories or '').lower()):
                    filtered_products.append(product)
                    
                    if len(filtered_products) >= limit:
                        break
            
            return filtered_products
            
        except Exception as e:
            logger.error(f"Erreur recherche produits: {e}")
            return []
    
    def get_products_by_category(self, category: str, limit: int = 20) -> List[Product]:
        """
        Récupère les produits par catégorie
        """
        try:
            all_products = list(Product.objects.all())
            category_lower = category.lower()
            
            filtered_products = []
            for product in all_products:
                if product.categories and category_lower in product.categories.lower():
                    filtered_products.append(product)
                    
                    if len(filtered_products) >= limit:
                        break
            
            return filtered_products
            
        except Exception as e:
            logger.error(f"Erreur récupération par catégorie: {e}")
            return []
    
    def get_products_by_nutriscore(self, grade: str, limit: int = 20) -> List[Product]:
        """
        Récupère les produits par grade Nutri-Score
        """
        try:
            return list(Product.objects.filter(nutriscore_grade=grade.upper()).limit(limit))
        except Exception as e:
            logger.error(f"Erreur récupération par Nutri-Score: {e}")
            return [] 