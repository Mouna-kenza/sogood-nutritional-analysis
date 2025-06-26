from fastapi import APIRouter, HTTPException, Query
from cassandra.cqlengine.query import DoesNotExist
from typing import Optional, List
import logging

from backend.models.product import Product
from backend.schemas.product import (
    ProductResponse, ProductSearchQuery, ProductSearchResponse,
    NutriscoreCalculationRequest, NutriscoreCalculationResponse,
    DatabaseStats, ProductSearchItem
)
from backend.services.nutriscore_service import NutriscoreService
from backend.services.search_service import SearchService
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Services
nutriscore_service = NutriscoreService()
search_service = SearchService()

# Mapping des catégories françaises vers anglaises
CATEGORY_MAPPING = {
    'petit-déjeuners': ['breakfast', 'cereals', 'bread', 'pastries'],
    'viandes et dérivés': ['meat', 'poultry', 'pork', 'beef', 'lamb'],
    'produits laitiers': ['dairy', 'milk', 'cheese', 'yogurt'],
    'boissons': ['beverages', 'drinks', 'juice', 'soda'],
    'snacks': ['snacks', 'crackers', 'chips', 'cookies'],
    'compléments alimentaires': ['supplements', 'vitamins'],
    'aliments végétaux': ['plant-based', 'vegetarian', 'vegan'],
    'condiments': ['condiments', 'sauces', 'spices']
}

def map_category_to_english(french_category: str) -> List[str]:
    """Mappe les catégories françaises vers les catégories dans la base de données"""
    mapping = {
        "condiments": ["condiments", "sauces", "groceries"],
        "épices": ["épices", "herbes", "assaisonnements"],
        "viandes": ["viandes", "viandes et dérivés", "poulet", "volailles", "charcuteries", "saucisses"],
        "céréales": ["céréales", "grains", "pain", "pâtes"],
        "légumes": ["légumes", "légumineuses"],
        "fruits": ["fruits", "baies"],
        "produits laitiers": ["produits laitiers", "lait", "fromages", "produits fermentés"],
        "boissons": ["boissons", "boissons gazeuses", "sodas", "carbonated drinks"],
        "snacks": ["snacks", "chips", "crackers"],
        "desserts": ["desserts", "bonbons", "chocolat", "dessert-vegetal"],
        "conserves": ["conserves", "préservés"],
        "fruits secs": ["noix", "fruits secs"],
        "poissons": ["poissons", "fruits de mer"],
        "œufs": ["œufs"],
        "huiles": ["huiles", "graisses"],
        "soupes": ["soupes", "bouillons"],
        "pâtes": ["pâtes", "noodles"],
        "riz": ["riz"],
        "farines": ["farines"],
        "sucre": ["sucre", "édulcorants"],
        "plats préparés": ["plats préparés", "pizzas", "tartes salées", "quiches"]
    }
    
    french_lower = french_category.lower().strip()
    
    # Retourner les catégories mappées si trouvées
    if french_lower in mapping:
        return mapping[french_lower]
    
    # Si pas trouvé, retourner la catégorie originale
    return [french_lower]

@router.get("/search", response_model=ProductSearchResponse)
def search_products(
    q: Optional[str] = Query(None, description="Terme de recherche"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    nutri_score: Optional[str] = Query(None, description="Filtrer par Nutri-Score"),
    nova_group: Optional[int] = Query(None, description="Filtrer par groupe NOVA"),
    complete_data: Optional[str] = Query("false", description="Filtrer les produits avec données complètes (true/false)"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Taille de page")
):
    """
    Recherche de produits avec filtres - Compatible avec le frontend Flask
    """
    try:
        # Debug: afficher le paramètre
        logger.info(f"Paramètre complete_data: {complete_data}")
        logger.info("Aucun filtre de données complètes appliqué - Tous les produits affichés")
        
        # Récupérer tous les produits (Cassandra ne supporte pas les requêtes complexes comme SQLAlchemy)
        all_products = list(Product.objects.all())
        
        # Filtrer en mémoire
        filtered_products = []
        for product in all_products:
            # Exclure les produits sans catégorie ou avec catégorie "Non classé"
            if not product.categories or product.categories.strip() == "" or "non classé" in product.categories.lower():
                continue
                
            # Filtre de recherche textuelle
            if q:
                search_term = q.lower()
                if not (search_term in (product.product_name or '').lower() or 
                       search_term in (product.brands or '').lower()):
                    continue
            
            # Filtre par catégorie
            if category and product.categories:
                # Utiliser le mapping français-anglais
                mapped_categories = map_category_to_english(category)
                product_categories_lower = product.categories.lower()
                
                # Vérifier si une des catégories mappées correspond
                category_matches = False
                for mapped_cat in mapped_categories:
                    if mapped_cat.lower() in product_categories_lower:
                        category_matches = True
                        break
                
                # Si pas de correspondance directe, vérifier les correspondances partielles
                if not category_matches:
                    product_categories_list = [cat.strip().lower() for cat in product.categories.split(',')]
                    if not any(any(mapped_cat.lower() in cat or cat in mapped_cat.lower() for mapped_cat in mapped_categories) 
                              for cat in product_categories_list):
                        continue
            
            # Filtre par Nutri-Score
            if nutri_score and product.nutriscore_grade != nutri_score.upper():
                continue
            
            # Filtre par groupe NOVA
            if nova_group and product.nova_group != nova_group:
                continue
            
            filtered_products.append(product)
        
        # Pagination
        total = len(filtered_products)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        products_page = filtered_products[start_idx:end_idx]
        
        products_data = []
        for product in products_page:
            controversies = []
            if product.sugars_100g and float(product.sugars_100g) > 22.5:
                controversies.append("Très riche en sucre")
            if product.saturated_fat_100g and float(product.saturated_fat_100g) > 5:
                controversies.append("Riche en graisses saturées")
            if product.salt_100g and float(product.salt_100g) > 1.5:
                controversies.append("Riche en sel")
                
            products_data.append(ProductSearchItem(
                id=product.code,
                name=product.product_name or 'Produit sans nom',
                brand=product.brands or 'Marque inconnue',
                category=(product.categories.split(',')[0].strip() if product.categories else 'Non classé'),
                nutri_score=product.nutriscore_grade or 'N/A',
                nova_score=product.nova_group or 0,
                sugar_100g=float(product.sugars_100g) if product.sugars_100g else 0,
                salt_100g=float(product.salt_100g) if product.salt_100g else 0,
                energy_100g=float(product.energy_kcal_100g) if product.energy_kcal_100g else 0,
                controversies=controversies,
                image_url=product.get_best_image_url()
            ))
            
        total_pages = (total + page_size - 1) // page_size
        return ProductSearchResponse(
            products=products_data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Erreur recherche produits: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche")

@router.get("/{product_code}", response_model=dict)
async def get_product(product_code: str):
    """
    Récupère un produit par son code - Compatible avec le frontend Flask
    """
    try:
        # Chercher le produit par code
        products = list(Product.objects.filter(code=product_code).limit(1))
        
        if not products:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        
        product = products[0]
        
        # Déterminer les controverses
        controversies = []
        if product.sugars_100g and float(product.sugars_100g) > 22.5:
            controversies.append("Très riche en sucre")
        if product.saturated_fat_100g and float(product.saturated_fat_100g) > 5:
            controversies.append("Riche en graisses saturées")
        if product.salt_100g and float(product.salt_100g) > 1.5:
            controversies.append("Riche en sel")
        if product.additives and len(product.additives.split(',')) > 5:
            controversies.append("Contient de nombreux additifs")
        
        # Format détaillé pour la page produit
        product_data = {
            'id': product.code,
            'code': product.code,
            'name': product.product_name or 'Produit sans nom',
            'brand': product.brands or 'Marque inconnue',
            'category': product.categories or 'Non classé',
            'nutri_score': product.nutriscore_grade or 'N/A',
            'nova_score': product.nova_group or 0,
            'images': {
                'main': product.image_url,
                'front': product.image_front_url,
                'ingredients': product.image_ingredients_url,
                'nutrition': product.image_nutrition_url,
                'best': product.get_best_image_url()
            },
            'nutrition': {
                'energy_100g': float(product.energy_kcal_100g) if product.energy_kcal_100g else 0,
                'fat_100g': float(product.fat_100g) if product.fat_100g else 0,
                'saturated_fat_100g': float(product.saturated_fat_100g) if product.saturated_fat_100g else 0,
                'carbohydrates_100g': float(product.carbohydrates_100g) if product.carbohydrates_100g else 0,
                'sugars_100g': float(product.sugars_100g) if product.sugars_100g else 0,
                'fiber_100g': float(product.fiber_100g) if product.fiber_100g else 0,
                'proteins_100g': float(product.proteins_100g) if product.proteins_100g else 0,
                'salt_100g': float(product.salt_100g) if product.salt_100g else 0,
            },
            'ingredients': product.ingredients_text,
            'allergens': product.allergens,
            'additives': product.additives,
            'controversies': controversies,
            'completeness': float(product.completeness) if product.completeness else 0,
            'countries': product.countries
        }
        
        return product_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération produit {product_code}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du produit")

@router.post("/calculate-nutriscore", response_model=NutriscoreCalculationResponse)
async def calculate_nutriscore(request: NutriscoreCalculationRequest):
    """
    Calcule le Nutri-Score pour des valeurs nutritionnelles données
    """
    try:
        score = nutriscore_service.calculate_nutriscore(
            energy_100g=request.energy_100g,
            fat_100g=request.fat_100g,
            saturated_fat_100g=request.saturated_fat_100g,
            carbohydrates_100g=0,  # Non utilisé dans le calcul Nutri-Score
            sugars_100g=request.sugars_100g,
            salt_100g=request.salt_100g,
            fiber_100g=request.fiber_100g,
            proteins_100g=request.proteins_100g
        )
        
        return NutriscoreCalculationResponse(
            nutriscore_grade=score['grade'],
            nutriscore_score=score['score'],
            details=score['details']
        )
    except Exception as e:
        logger.error(f"Erreur calcul Nutri-Score: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du calcul du Nutri-Score")

@router.get("/stats/database", response_model=DatabaseStats)
async def get_database_stats():
    """
    Statistiques de la base de données
    """
    try:
        # Compter tous les produits
        total_products = Product.objects.count()
        
        # Compter par Nutri-Score
        nutriscore_stats = {}
        for grade in ['A', 'B', 'C', 'D', 'E']:
            count = Product.objects.filter(nutriscore_grade=grade).count()
            nutriscore_stats[grade] = count
        
        # Compter par groupe NOVA
        nova_stats = {}
        for group in [1, 2, 3, 4]:
            count = Product.objects.filter(nova_group=group).count()
            nova_stats[f"NOVA {group}"] = count
        
        return DatabaseStats(
            total_products=total_products,
            products_with_nutriscore=sum(nutriscore_stats.values()),
            products_with_nutrition=total_products,  # Simplification
            nutriscore_distribution=nutriscore_stats,
            nova_distribution=nova_stats,
            top_brands=[],  # Simplification pour Cassandra
            top_categories=[]  # Simplification pour Cassandra
        )
    except Exception as e:
        logger.error(f"Erreur statistiques base de données: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des statistiques")

@router.get("", response_model=ProductSearchResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    complete_data: Optional[str] = Query("false", description="Filtrer les produits avec données complètes (true/false)")
):
    """
    Liste tous les produits avec pagination
    """
    try:
        # Récupérer tous les produits
        all_products = list(Product.objects.all())
        
        # Pagination
        total = len(all_products)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        products_page = all_products[start_idx:end_idx]
        
        products_data = []
        for product in products_page:
            controversies = []
            if product.sugars_100g and float(product.sugars_100g) > 22.5:
                controversies.append("Très riche en sucre")
            if product.saturated_fat_100g and float(product.saturated_fat_100g) > 5:
                controversies.append("Riche en graisses saturées")
            if product.salt_100g and float(product.salt_100g) > 1.5:
                controversies.append("Riche en sel")
                
            products_data.append(ProductSearchItem(
                id=product.code,
                name=product.product_name or 'Produit sans nom',
                brand=product.brands or 'Marque inconnue',
                category=(product.categories.split(',')[0].strip() if product.categories else 'Non classé'),
                nutri_score=product.nutriscore_grade or 'N/A',
                nova_score=product.nova_group or 0,
                sugar_100g=float(product.sugars_100g) if product.sugars_100g else 0,
                salt_100g=float(product.salt_100g) if product.salt_100g else 0,
                energy_100g=float(product.energy_kcal_100g) if product.energy_kcal_100g else 0,
                controversies=controversies,
                image_url=product.get_best_image_url()
            ))
        
        total_pages = (total + page_size - 1) // page_size
        return ProductSearchResponse(
            products=products_data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Erreur liste produits: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des produits") 