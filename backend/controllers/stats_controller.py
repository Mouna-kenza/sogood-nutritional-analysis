from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import requests
from collections import Counter
import pandas as pd

router = APIRouter(prefix="/api/stats", tags=["statistics"])

@router.get("/overview")
async def get_overview_stats() -> Dict[str, Any]:
    """Récupère les statistiques générales de la base de données"""
    try:
        # Récupérer le nombre total de produits
        response = requests.get("http://localhost:8000/api/products/search?q=&page=1&page_size=1")
        data = response.json()
        total_products = data.get('total', 0)
        
        # Récupérer un échantillon pour les statistiques
        response = requests.get("http://localhost:8000/api/products/search?q=&page=1&page_size=1000")
        data = response.json()
        products = data.get('products', [])
        
        if not products:
            return {
                "total_products": 0,
                "categories": {},
                "nutri_scores": {},
                "brands": {},
                "quality_stats": {},
                "nova_scores": {},
                "nutrition_averages": {}
            }
        
        df = pd.DataFrame(products)
        
        # Nettoyer les données
        df['category'] = df['category'].fillna('Non classé')
        df['brand'] = df['brand'].fillna('Marque inconnue')
        df['nutri_score'] = df['nutri_score'].fillna('N/A')
        df['nova_score'] = df['nova_score'].fillna(0)
        
        # Statistiques de qualité
        quality_stats = {
            'with_images': int(df['image_url'].notna().sum()),
            'with_nutrition_data': int(df['energy_100g'].notna().sum()),
            'with_brand_info': int((df['brand'] != 'Marque inconnue').sum()),
            'with_category_info': int((df['category'] != 'Non classé').sum())
        }
        
        # Moyennes nutritionnelles
        nutrition_averages = {
            'avg_energy': float(df['energy_100g'].mean()) if df['energy_100g'].notna().any() else 0,
            'avg_fat': float(df['fat_100g'].mean()) if df['fat_100g'].notna().any() else 0,
            'avg_proteins': float(df['proteins_100g'].mean()) if df['proteins_100g'].notna().any() else 0,
            'avg_sugar': float(df['sugar_100g'].mean()) if df['sugar_100g'].notna().any() else 0,
            'avg_salt': float(df['salt_100g'].mean()) if df['salt_100g'].notna().any() else 0
        }
        
        return {
            "total_products": total_products,
            "categories": df['category'].value_counts().head(10).to_dict(),
            "nutri_scores": df['nutri_score'].value_counts().to_dict(),
            "brands": df['brand'].value_counts().head(10).to_dict(),
            "quality_stats": quality_stats,
            "nova_scores": df['nova_score'].value_counts().to_dict(),
            "nutrition_averages": nutrition_averages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")

@router.get("/categories")
async def get_category_stats() -> Dict[str, Any]:
    """Récupère les statistiques détaillées par catégorie"""
    try:
        response = requests.get("http://localhost:8000/api/products/search?q=&page=1&page_size=2000")
        data = response.json()
        products = data.get('products', [])
        
        if not products:
            return {"categories": {}}
        
        df = pd.DataFrame(products)
        df['category'] = df['category'].fillna('Non classé')
        df['nutri_score'] = df['nutri_score'].fillna('N/A')
        
        # Statistiques par catégorie
        category_stats = {}
        
        for category in df['category'].unique():
            cat_df = df[df['category'] == category]
            
            category_stats[category] = {
                "count": int(len(cat_df)),
                "nutri_score_distribution": cat_df['nutri_score'].value_counts().to_dict(),
                "avg_energy": float(cat_df['energy_100g'].mean()) if cat_df['energy_100g'].notna().any() else 0,
                "avg_fat": float(cat_df['fat_100g'].mean()) if cat_df['fat_100g'].notna().any() else 0,
                "avg_proteins": float(cat_df['proteins_100g'].mean()) if cat_df['proteins_100g'].notna().any() else 0,
                "avg_sugar": float(cat_df['sugar_100g'].mean()) if cat_df['sugar_100g'].notna().any() else 0,
                "avg_salt": float(cat_df['salt_100g'].mean()) if cat_df['salt_100g'].notna().any() else 0,
                "with_images": int(cat_df['image_url'].notna().sum()),
                "with_nutrition_data": int(cat_df['energy_100g'].notna().sum())
            }
        
        return {"categories": category_stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques par catégorie: {str(e)}")

@router.get("/brands")
async def get_brand_stats() -> Dict[str, Any]:
    """Récupère les statistiques détaillées par marque"""
    try:
        response = requests.get("http://localhost:8000/api/products/search?q=&page=1&page_size=2000")
        data = response.json()
        products = data.get('products', [])
        
        if not products:
            return {"brands": {}}
        
        df = pd.DataFrame(products)
        df['brand'] = df['brand'].fillna('Marque inconnue')
        df['nutri_score'] = df['nutri_score'].fillna('N/A')
        
        # Filtrer les marques avec au moins 2 produits
        brand_counts = df['brand'].value_counts()
        significant_brands = brand_counts[brand_counts >= 2].index
        
        brand_stats = {}
        
        for brand in significant_brands:
            brand_df = df[df['brand'] == brand]
            
            brand_stats[brand] = {
                "count": int(len(brand_df)),
                "nutri_score_distribution": brand_df['nutri_score'].value_counts().to_dict(),
                "avg_energy": float(brand_df['energy_100g'].mean()) if brand_df['energy_100g'].notna().any() else 0,
                "avg_fat": float(brand_df['fat_100g'].mean()) if brand_df['fat_100g'].notna().any() else 0,
                "avg_proteins": float(brand_df['proteins_100g'].mean()) if brand_df['proteins_100g'].notna().any() else 0,
                "avg_sugar": float(brand_df['sugar_100g'].mean()) if brand_df['sugar_100g'].notna().any() else 0,
                "avg_salt": float(brand_df['salt_100g'].mean()) if brand_df['salt_100g'].notna().any() else 0,
                "categories": brand_df['category'].value_counts().head(5).to_dict()
            }
        
        return {"brands": brand_stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques par marque: {str(e)}")

@router.get("/nutrition")
async def get_nutrition_stats() -> Dict[str, Any]:
    """Récupère les statistiques nutritionnelles détaillées"""
    try:
        response = requests.get("http://localhost:8000/api/products/search?q=&page=1&page_size=2000")
        data = response.json()
        products = data.get('products', [])
        
        if not products:
            return {"nutrition": {}}
        
        df = pd.DataFrame(products)
        
        # Statistiques nutritionnelles
        nutrition_stats = {
            "energy_ranges": {
                "low": int((df['energy_100g'] < 100).sum()),
                "medium": int(((df['energy_100g'] >= 100) & (df['energy_100g'] < 300)).sum()),
                "high": int((df['energy_100g'] >= 300).sum())
            },
            "fat_ranges": {
                "low": int((df['fat_100g'] < 3).sum()),
                "medium": int(((df['fat_100g'] >= 3) & (df['fat_100g'] < 20)).sum()),
                "high": int((df['fat_100g'] >= 20).sum())
            },
            "sugar_ranges": {
                "low": int((df['sugar_100g'] < 5).sum()),
                "medium": int(((df['sugar_100g'] >= 5) & (df['sugar_100g'] < 15)).sum()),
                "high": int((df['sugar_100g'] >= 15).sum())
            },
            "salt_ranges": {
                "low": int((df['salt_100g'] < 0.3).sum()),
                "medium": int(((df['salt_100g'] >= 0.3) & (df['salt_100g'] < 1.5)).sum()),
                "high": int((df['salt_100g'] >= 1.5).sum())
            },
            "averages": {
                "energy": float(df['energy_100g'].mean()) if df['energy_100g'].notna().any() else 0,
                "fat": float(df['fat_100g'].mean()) if df['fat_100g'].notna().any() else 0,
                "proteins": float(df['proteins_100g'].mean()) if df['proteins_100g'].notna().any() else 0,
                "sugar": float(df['sugar_100g'].mean()) if df['sugar_100g'].notna().any() else 0,
                "salt": float(df['salt_100g'].mean()) if df['salt_100g'].notna().any() else 0
            }
        }
        
        return {"nutrition": nutrition_stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques nutritionnelles: {str(e)}") 