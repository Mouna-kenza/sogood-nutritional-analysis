from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
from typing import List, Optional, Dict, Any, Tuple
import logging
from backend.models.product import Product

logger = logging.getLogger(__name__)

class SearchService:
    """
    Service de recherche avancée pour les produits
    """
    
    def __init__(self):
        self.search_weights = {
            'product_name': 3.0,
            'brands': 2.0,
            'categories': 1.5,
            'ingredients': 1.0
        }
    
    def search_products(
        self,
        db: Session,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "relevance"
    ) -> Tuple[List[Product], int]:
        """
        Recherche avancée de produits
        
        Args:
            db: Session de base de données
            query: Terme de recherche
            filters: Dictionnaire de filtres
            page: Numéro de page
            page_size: Taille de page
            sort_by: Critère de tri
            
        Returns:
            Tuple[List[Product], int]: (produits, total)
        """
        try:
            # Construction de la requête de base
            base_query = db.query(Product)
            
            # Application des filtres de recherche textuelle
            if query:
                base_query = self._apply_text_search(base_query, query)
            
            # Application des filtres
            if filters:
                base_query = self._apply_filters(base_query, filters)
            
            # Compter le total
            total = base_query.count()
            
            # Application du tri
            base_query = self._apply_sorting(base_query, sort_by, query)
            
            # Pagination
            offset = (page - 1) * page_size
            products = base_query.offset(offset).limit(page_size).all()
            
            return products, total
            
        except Exception as e:
            logger.error(f"Erreur recherche produits: {e}")
            raise
    
    def _apply_text_search(self, query, search_term: str):
        """
        Applique la recherche textuelle
        """
        search_pattern = f"%{search_term.lower()}%"
        
        return query.filter(
            or_(
                func.lower(Product.product_name).like(search_pattern),
                func.lower(Product.brands).like(search_pattern),
                func.lower(Product.categories).like(search_pattern),
                func.lower(Product.ingredients_text).like(search_pattern)
            )
        )
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Applique les filtres sur la requête
        """
        if 'nutriscore_grade' in filters and filters['nutriscore_grade']:
            query = query.filter(Product.nutriscore_grade == filters['nutriscore_grade'].upper())
        
        if 'nova_group' in filters and filters['nova_group']:
            query = query.filter(Product.nova_group == filters['nova_group'])
        
        if 'category' in filters and filters['category']:
            category_pattern = f"%{filters['category'].lower()}%"
            query = query.filter(func.lower(Product.categories).like(category_pattern))
        
        if 'brand' in filters and filters['brand']:
            brand_pattern = f"%{filters['brand'].lower()}%"
            query = query.filter(func.lower(Product.brands).like(brand_pattern))
        
        if 'min_completeness' in filters and filters['min_completeness']:
            query = query.filter(Product.completeness >= filters['min_completeness'])
        
        if 'has_nutrition' in filters and filters['has_nutrition']:
            query = query.filter(Product.energy_100g.isnot(None))
        
        if 'countries' in filters and filters['countries']:
            countries_pattern = f"%{filters['countries'].lower()}%"
            query = query.filter(func.lower(Product.countries).like(countries_pattern))
        
        return query
    
    def _apply_sorting(self, query, sort_by: str, search_term: Optional[str] = None):
        """
        Applique le tri sur la requête
        """
        if sort_by == "relevance" and search_term:
            # Tri par pertinence (approximatif)
            return query.order_by(Product.completeness.desc(), Product.id)
        elif sort_by == "name":
            return query.order_by(Product.product_name)
        elif sort_by == "nutriscore":
            return query.order_by(Product.nutriscore_grade, Product.nutriscore_score)
        elif sort_by == "nova":
            return query.order_by(Product.nova_group)
        elif sort_by == "completeness":
            return query.order_by(Product.completeness.desc())
        elif sort_by == "recent":
            return query.order_by(Product.updated_at.desc())
        else:
            return query.order_by(Product.id)
    
    def get_suggestions(self, db: Session, partial_query: str, limit: int = 5) -> List[str]:
        """
        Obtient des suggestions de recherche
        """
        try:
            search_pattern = f"{partial_query.lower()}%"
            
            # Suggestions de noms de produits
            product_suggestions = db.query(Product.product_name).filter(
                func.lower(Product.product_name).like(search_pattern),
                Product.product_name.isnot(None)
            ).distinct().limit(limit).all()
            
            # Suggestions de marques
            brand_suggestions = db.query(Product.brands).filter(
                func.lower(Product.brands).like(search_pattern),
                Product.brands.isnot(None)
            ).distinct().limit(limit).all()
            
            suggestions = []
            suggestions.extend([prod[0] for prod in product_suggestions])
            suggestions.extend([brand[0] for brand in brand_suggestions])
            
            return list(set(suggestions))[:limit]
            
        except Exception as e:
            logger.error(f"Erreur suggestions: {e}")
            return []
    
    def get_popular_searches(self, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtient les recherches populaires basées sur les données
        """
        try:
            # Top marques
            popular_brands = db.query(
                Product.brands,
                func.count(Product.id).label('count')
            ).filter(
                Product.brands.isnot(None)
            ).group_by(Product.brands).order_by(
                func.count(Product.id).desc()
            ).limit(limit).all()
            
            # Top catégories
            popular_categories = db.query(
                func.split_part(Product.categories, ',', 1).label('category'),
                func.count(Product.id).label('count')
            ).filter(
                Product.categories.isnot(None)
            ).group_by(
                func.split_part(Product.categories, ',', 1)
            ).order_by(
                func.count(Product.id).desc()
            ).limit(limit).all()
            
            return {
                'brands': [{'name': brand, 'count': count} for brand, count in popular_brands],
                'categories': [{'name': cat, 'count': count} for cat, count in popular_categories]
            }
            
        except Exception as e:
            logger.error(f"Erreur recherches populaires: {e}")
            return {'brands': [], 'categories': []} 