from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class NutritionData(BaseModel):
    """Données nutritionnelles pour 100g"""
    energy_100g: Optional[float] = Field(None, description="Énergie en kJ pour 100g")
    energy_kcal_100g: Optional[float] = Field(None, description="Énergie en kcal pour 100g")
    fat_100g: Optional[float] = Field(None, description="Lipides pour 100g")
    saturated_fat_100g: Optional[float] = Field(None, description="Acides gras saturés pour 100g")
    carbohydrates_100g: Optional[float] = Field(None, description="Glucides pour 100g")
    sugars_100g: Optional[float] = Field(None, description="Sucres pour 100g")
    fiber_100g: Optional[float] = Field(None, description="Fibres pour 100g")
    proteins_100g: Optional[float] = Field(None, description="Protéines pour 100g")
    salt_100g: Optional[float] = Field(None, description="Sel pour 100g")
    sodium_100g: Optional[float] = Field(None, description="Sodium pour 100g")

class NutritionalScores(BaseModel):
    """Scores nutritionnels"""
    nutriscore_grade: Optional[str] = Field(None, description="Grade Nutri-Score (A-E)")
    nutriscore_score: Optional[int] = Field(None, description="Score Nutri-Score numérique")
    nova_group: Optional[int] = Field(None, description="Groupe NOVA (1-4)")
    
    @validator('nutriscore_grade')
    def validate_nutriscore_grade(cls, v):
        if v and v not in ['A', 'B', 'C', 'D', 'E']:
            raise ValueError('Nutri-Score doit être A, B, C, D ou E')
        return v
    
    @validator('nova_group')
    def validate_nova_group(cls, v):
        if v and not (1 <= v <= 4):
            raise ValueError('Groupe NOVA doit être entre 1 et 4')
        return v

class ProductBase(BaseModel):
    """Schéma de base pour un produit"""
    code: str = Field(..., description="Code-barres du produit", min_length=1, max_length=50)
    product_name: Optional[str] = Field(None, description="Nom du produit", max_length=500)
    brands: Optional[str] = Field(None, description="Marques", max_length=300)
    categories: Optional[str] = Field(None, description="Catégories", max_length=1000)
    countries: Optional[str] = Field(None, description="Pays", max_length=200)
    ingredients_text: Optional[str] = Field(None, description="Liste des ingrédients")
    allergens: Optional[str] = Field(None, description="Allergènes", max_length=500)
    additives: Optional[str] = Field(None, description="Additifs", max_length=500)

class ProductCreate(ProductBase):
    """Schéma pour créer un produit"""
    nutrition: Optional[NutritionData] = None
    scores: Optional[NutritionalScores] = None

class ProductUpdate(BaseModel):
    """Schéma pour mettre à jour un produit"""
    product_name: Optional[str] = Field(None, max_length=500)
    brands: Optional[str] = Field(None, max_length=300)
    categories: Optional[str] = Field(None, max_length=1000)
    countries: Optional[str] = Field(None, max_length=200)
    nutrition: Optional[NutritionData] = None
    scores: Optional[NutritionalScores] = None
    ingredients_text: Optional[str] = None
    allergens: Optional[str] = Field(None, max_length=500)
    additives: Optional[str] = Field(None, max_length=500)

class ProductResponse(ProductBase):
    """Schéma de réponse pour un produit"""
    id: int
    nutrition: NutritionData
    scores: NutritionalScores
    completeness: Optional[float] = Field(None, description="Complétude des données (%)")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductSearchQuery(BaseModel):
    """Paramètres de recherche de produits"""
    query: Optional[str] = Field(None, description="Terme de recherche")
    brands: Optional[str] = Field(None, description="Filtrer par marques")
    categories: Optional[str] = Field(None, description="Filtrer par catégories")
    nutriscore_grade: Optional[str] = Field(None, description="Filtrer par Nutri-Score")
    nova_group: Optional[int] = Field(None, description="Filtrer par groupe NOVA")
    min_completeness: Optional[float] = Field(None, description="Complétude minimale (%)")
    page: int = Field(1, description="Numéro de page", ge=1)
    page_size: int = Field(20, description="Taille de page", ge=1, le=100)
    
    @validator('nutriscore_grade')
    def validate_nutriscore_filter(cls, v):
        if v and v not in ['A', 'B', 'C', 'D', 'E']:
            raise ValueError('Nutri-Score doit être A, B, C, D ou E')
        return v

class ProductSearchItem(BaseModel):
    """Produit simplifié pour la recherche"""
    id: str
    name: str
    brand: str
    category: str
    nutri_score: str
    nova_score: int
    sugar_100g: float
    salt_100g: float
    energy_100g: float
    controversies: List[str]
    image_url: Optional[str] = Field(None, description="URL de l'image du produit")

class ProductSearchResponse(BaseModel):
    """Réponse de recherche de produits"""
    products: List[ProductSearchItem]
    total: int
    page: int
    page_size: int
    total_pages: int

class NutriscoreCalculationRequest(BaseModel):
    """Demande de calcul de Nutri-Score"""
    energy_100g: float = Field(..., description="Énergie en kJ pour 100g")
    fat_100g: float = Field(..., description="Lipides pour 100g")
    saturated_fat_100g: float = Field(..., description="Acides gras saturés pour 100g")
    sugars_100g: float = Field(..., description="Sucres pour 100g")
    salt_100g: float = Field(..., description="Sel pour 100g")
    fiber_100g: Optional[float] = Field(0, description="Fibres pour 100g")
    proteins_100g: Optional[float] = Field(0, description="Protéines pour 100g")
    fruits_vegetables_nuts_percent: Optional[float] = Field(0, description="% fruits, légumes, noix")

class NutriscoreCalculationResponse(BaseModel):
    """Réponse de calcul de Nutri-Score"""
    nutriscore_grade: str = Field(..., description="Grade Nutri-Score (A-E)")
    nutriscore_score: int = Field(..., description="Score Nutri-Score numérique")
    details: Dict[str, Any] = Field(..., description="Détails du calcul")

class MLPredictionRequest(BaseModel):
    """Demande de prédiction ML"""
    nutrition_data: NutritionData
    product_info: Optional[Dict[str, Any]] = None

class MLPredictionResponse(BaseModel):
    """Réponse de prédiction ML"""
    predicted_nutriscore: str
    confidence: float
    probabilities: Dict[str, float]

class DatabaseStats(BaseModel):
    """Statistiques de la base de données"""
    total_products: int
    products_with_nutriscore: int
    products_with_nutrition: int
    nutriscore_distribution: Dict[str, int]
    nova_distribution: Dict[str, int]
    top_brands: List[Dict[str, Any]]
    top_categories: List[Dict[str, Any]] 