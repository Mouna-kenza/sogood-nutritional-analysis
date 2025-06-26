from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from backend.models.product import Product
from backend.database import setup_cassandra_connection
from decimal import Decimal
import logging

router = APIRouter(tags=["statistics"])

@router.get("/overview")
async def get_overview_stats() -> Dict[str, Any]:
    """Récupère les statistiques générales de la base de données"""
    try:
        # Initialiser la connexion Cassandra
        setup_cassandra_connection()
        
        logging.info("🔄 Début de la récupération des statistiques...")
        
        # Compter le total de produits (requête optimisée)
        total_products = Product.objects.count()
        logging.info(f"📊 Total de produits: {total_products}")
        
        # Utiliser des requêtes limitées pour éviter les timeouts
        sample_size = min(1000, total_products)
        products = list(Product.objects.limit(sample_size))
        logging.info(f"📋 Échantillon de {len(products)} produits analysé")
        
        # Statistiques des catégories
        categories = {}
        for product in products:
            if product.categories and product.categories != "undefined":
                cat = product.categories.split(',')[0].strip()
                if cat and cat != "undefined":
                    categories[cat] = categories.get(cat, 0) + 1
        
        # Statistiques des marques
        brands = {}
        for product in products:
            if product.brands and product.brands != "None":
                brand = product.brands.split(',')[0].strip()
                if brand and brand != "None":
                    brands[brand] = brands.get(brand, 0) + 1
        
        # Statistiques Nutri-Score
        nutri_scores = {}
        for product in products:
            if product.nutriscore_grade:
                grade = product.nutriscore_grade
                nutri_scores[grade] = nutri_scores.get(grade, 0) + 1
        
        # Statistiques NOVA
        nova_scores = {}
        for product in products:
            if product.nova_group:
                nova_scores[str(product.nova_group)] = nova_scores.get(str(product.nova_group), 0) + 1
        
        # Statistiques de qualité
        with_images = sum(1 for p in products if p.has_images)
        with_nutrition_data = sum(1 for p in products if p.nutrition_available)
        
        # Moyennes nutritionnelles
        energy_values = [float(p.energy_100g) for p in products if p.energy_100g]
        fat_values = [float(p.fat_100g) for p in products if p.fat_100g]
        protein_values = [float(p.proteins_100g) for p in products if p.proteins_100g]
        sugar_values = [float(p.sugars_100g) for p in products if p.sugars_100g]
        salt_values = [float(p.salt_100g) for p in products if p.salt_100g]
        
        nutrition_averages = {
            "avg_energy": round(sum(energy_values) / len(energy_values), 1) if energy_values else 0,
            "avg_fat": round(sum(fat_values) / len(fat_values), 1) if fat_values else 0,
            "avg_proteins": round(sum(protein_values) / len(protein_values), 1) if protein_values else 0,
            "avg_sugar": round(sum(sugar_values) / len(sugar_values), 1) if sugar_values else 0,
            "avg_salt": round(sum(salt_values) / len(salt_values), 2) if salt_values else 0
        }
        
        result = {
            "total_products": total_products,
            "categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]),
            "nutri_scores": nutri_scores,
            "brands": dict(sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]),
            "quality_stats": {
                "with_images": with_images,
                "with_nutrition_data": with_nutrition_data
            },
            "nova_scores": nova_scores,
            "nutrition_averages": nutrition_averages
        }
        
        logging.info(f"✅ Statistiques générées: {len(categories)} catégories, {len(brands)} marques")
        return result
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de la récupération des statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")

@router.get("/export-csv")
async def export_csv():
    """Exporte les données pour Power BI"""
    try:
        # Initialiser la connexion Cassandra
        setup_cassandra_connection()
        
        csv_content = "id,name,brand,category,nutri_score,nova_score,energy_100g,fat_100g,proteins_100g,sugar_100g,salt_100g\n"
        
        # Récupérer les produits pour l'export
        products = list(Product.objects.limit(1000))  # Limiter à 1000 pour éviter les timeouts
        
        for product in products:
            # Nettoyer les données pour CSV
            name = product.product_name.replace('"', '""') if product.product_name else ""
            brand = product.brands.replace('"', '""') if product.brands else ""
            category = product.categories.split(',')[0].strip().replace('"', '""') if product.categories else ""
            
            csv_content += f'"{product.code}","{name}","{brand}","{category}","{product.nutriscore_grade or ""}","{product.nova_group or ""}","{product.energy_100g or ""}","{product.fat_100g or ""}","{product.proteins_100g or ""}","{product.sugars_100g or ""}","{product.salt_100g or ""}"\n'
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=sogood_products.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export: {str(e)}") 