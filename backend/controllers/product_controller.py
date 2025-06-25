from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
import logging

from backend.database import get_db
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

@router.get("/search", response_model=ProductSearchResponse)
def search_products(
    q: Optional[str] = Query(None, description="Terme de recherche"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    nutri_score: Optional[str] = Query(None, description="Filtrer par Nutri-Score"),
    nova_group: Optional[int] = Query(None, description="Filtrer par groupe NOVA"),
    complete_data: Optional[str] = Query("false", description="Filtrer les produits avec données complètes (true/false)"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Taille de page"),
    db: Session = Depends(get_db)
):
    """
    Recherche de produits avec filtres - Compatible avec le frontend Flask
    """
    try:
        query = db.query(Product)
        
        # Debug: afficher le paramètre
        logger.info(f"Paramètre complete_data: {complete_data}")
        
        # Filtre pour les données complètes - DÉSACTIVÉ
        # if complete_data == "true":
        #     logger.info("Application du filtre données complètes")
        #     query = query.filter(
        #         Product.product_name.isnot(None),
        #         Product.product_name != '',
        #         Product.brands.isnot(None),
        #         Product.brands != '',
        #         Product.nutriscore_grade.isnot(None),
        #         Product.nutriscore_grade != '',
        #         Product.nutriscore_grade != 'N/A',
        #         Product.energy_kcal_100g.isnot(None),
        #         Product.energy_kcal_100g > 0,
        #         Product.fat_100g.isnot(None),
        #         Product.fat_100g > 0,
        #         Product.sugars_100g.isnot(None),
        #         Product.sugars_100g > 0,
        #         Product.salt_100g.isnot(None),
        #         Product.salt_100g > 0,
        #         Product.proteins_100g.isnot(None),
        #         Product.proteins_100g > 0
        #     )
        #     logger.info(f"Nombre de produits après filtre: {query.count()}")
        # else:
        logger.info("Aucun filtre de données complètes appliqué - Tous les produits affichés")
        
        if q:
            search_term = f"%{q.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Product.product_name).like(search_term),
                    func.lower(Product.brands).like(search_term)
                )
            )
        if category:
            query = query.filter(
                or_(
                    func.lower(Product.categories).like(f"{category.lower()}%"),
                    func.lower(Product.categories).like(f"%{category.lower()}%")
                )
            )
        if nutri_score:
            query = query.filter(Product.nutriscore_grade == nutri_score.upper())
        if nova_group:
            query = query.filter(Product.nova_group == nova_group)
            
        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()
        
        products_data = []
        for product in products:
            controversies = []
            if product.sugars_100g and product.sugars_100g > 22.5:
                controversies.append("Très riche en sucre")
            if product.saturated_fat_100g and product.saturated_fat_100g > 5:
                controversies.append("Riche en graisses saturées")
            if product.salt_100g and product.salt_100g > 1.5:
                controversies.append("Riche en sel")
                
            products_data.append(ProductSearchItem(
                id=str(product.id),
                name=product.product_name or 'Produit sans nom',
                brand=product.brands or 'Marque inconnue',
                category=(product.categories.split(',')[0] if product.categories else 'Non classé'),
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

@router.get("/{product_id}", response_model=dict)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Récupère un produit par son ID - Compatible avec le frontend Flask
    """
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        
        # Déterminer les controverses
        controversies = []
        if product.sugars_100g and product.sugars_100g > 22.5:
            controversies.append("Très riche en sucre")
        if product.saturated_fat_100g and product.saturated_fat_100g > 5:
            controversies.append("Riche en graisses saturées")
        if product.salt_100g and product.salt_100g > 1.5:
            controversies.append("Riche en sel")
        if product.additives and len(product.additives.split(',')) > 5:
            controversies.append("Contient de nombreux additifs")
        
        # Format détaillé pour la page produit
        product_data = {
            'id': str(product.id),
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
        logger.error(f"Erreur récupération produit {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du produit")

@router.post("/calculate-nutriscore", response_model=NutriscoreCalculationResponse)
async def calculate_nutriscore(request: NutriscoreCalculationRequest):
    """
    Calcule le Nutri-Score pour des valeurs nutritionnelles données
    """
    try:
        result = nutriscore_service.calculate_nutriscore(
            energy_100g=request.energy_100g,
            fat_100g=0,  # Non utilisé dans le calcul
            saturated_fat_100g=request.saturated_fat_100g,
            carbohydrates_100g=0,  # Non utilisé directement
            sugars_100g=request.sugars_100g,
            fiber_100g=request.fiber_100g,
            proteins_100g=request.proteins_100g,
            salt_100g=request.salt_100g,
            fruits_vegetables_nuts_percent=request.fruits_vegetables_nuts_percent
        )
        
        return NutriscoreCalculationResponse(
            nutriscore_grade=result['nutriscore_grade'],
            nutriscore_score=result['nutriscore_score'],
            details=result['details']
        )
        
    except Exception as e:
        logger.error(f"Erreur calcul Nutri-Score: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats/database", response_model=DatabaseStats)
async def get_database_stats(db: Session = Depends(get_db)):
    """
    Statistiques de la base de données
    """
    try:
        # Comptes de base
        total_products = db.query(Product).count()
        products_with_nutriscore = db.query(Product).filter(Product.nutriscore_grade.isnot(None)).count()
        products_with_nutrition = db.query(Product).filter(Product.energy_100g.isnot(None)).count()
        
        # Distribution Nutri-Score
        nutriscore_dist = {}
        for grade in ['A', 'B', 'C', 'D', 'E']:
            count = db.query(Product).filter(Product.nutriscore_grade == grade).count()
            nutriscore_dist[grade] = count
        
        # Distribution NOVA
        nova_dist = {}
        for group in [1, 2, 3, 4]:
            count = db.query(Product).filter(Product.nova_group == group).count()
            nova_dist[str(group)] = count
        
        # Top marques
        top_brands_query = db.query(
            Product.brands, 
            func.count(Product.id).label('count')
        ).filter(
            Product.brands.isnot(None)
        ).group_by(Product.brands).order_by(func.count(Product.id).desc()).limit(10)
        
        top_brands = [{'name': brand, 'count': count} for brand, count in top_brands_query.all()]
        
        # Top catégories (première catégorie seulement)
        top_categories_query = db.query(
            func.split_part(Product.categories, ',', 1).label('category'),
            func.count(Product.id).label('count')
        ).filter(
            Product.categories.isnot(None)
        ).group_by(func.split_part(Product.categories, ',', 1)).order_by(func.count(Product.id).desc()).limit(10)
        
        top_categories = [{'name': category, 'count': count} for category, count in top_categories_query.all()]
        
        return DatabaseStats(
            total_products=total_products,
            products_with_nutriscore=products_with_nutriscore,
            products_with_nutrition=products_with_nutrition,
            nutriscore_distribution=nutriscore_dist,
            nova_distribution=nova_dist,
            top_brands=top_brands,
            top_categories=top_categories
        )
        
    except Exception as e:
        logger.error(f"Erreur statistiques: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du calcul des statistiques")

@router.get("", response_model=ProductSearchResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    complete_data: Optional[str] = Query("false", description="Filtrer les produits avec données complètes (true/false)"),
    db: Session = Depends(get_db)
):
    """
    Liste tous les produits avec pagination
    """
    try:
        db_query = db.query(Product)
        
        # Debug: afficher le paramètre
        logger.info(f"Paramètre complete_data: {complete_data}")
        
        # Filtre pour les données complètes - DÉSACTIVÉ
        # if complete_data == "true":
        #     logger.info("Application du filtre données complètes")
        #     db_query = db_query.filter(
        #         Product.product_name.isnot(None),
        #         Product.product_name != '',
        #         Product.brands.isnot(None),
        #         Product.brands != '',
        #         Product.nutriscore_grade.isnot(None),
        #         Product.nutriscore_grade != '',
        #         Product.nutriscore_grade != 'N/A',
        #         Product.energy_kcal_100g.isnot(None),
        #         Product.energy_kcal_100g > 0,
        #         Product.fat_100g.isnot(None),
        #         Product.fat_100g > 0,
        #         Product.sugars_100g.isnot(None),
        #         Product.sugars_100g > 0,
        #         Product.salt_100g.isnot(None),
        #         Product.salt_100g > 0,
        #         Product.proteins_100g.isnot(None),
        #         Product.proteins_100g > 0
        #     )
        #     logger.info(f"Nombre de produits après filtre: {db_query.count()}")
        # else:
        logger.info("Aucun filtre de données complètes appliqué - Tous les produits affichés")
        
        total = db_query.count()
        offset = (page - 1) * page_size
        products = db_query.offset(offset).limit(page_size).all()
        
        products_data = []
        for product in products:
            controversies = []
            if product.sugars_100g and product.sugars_100g > 22.5:
                controversies.append("Très riche en sucre")
            if product.saturated_fat_100g and product.saturated_fat_100g > 5:
                controversies.append("Riche en graisses saturées")
            if product.salt_100g and product.salt_100g > 1.5:
                controversies.append("Riche en sel")
            products_data.append(ProductSearchItem(
                id=str(product.id),
                name=product.product_name or 'Produit sans nom',
                brand=product.brands or 'Marque inconnue',
                category=(product.categories.split(',')[0] if product.categories else 'Non classé'),
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