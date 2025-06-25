import logging
from sqlalchemy import text
from backend.database import engine, SessionLocal
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimize_database():
    """
    Optimise la base de données PostgreSQL pour de meilleures performances
    """
    logger.info("🔧 Début de l'optimisation de la base de données")
    
    optimizations = [
        # Index pour la recherche textuelle
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_product_search ON products USING gin(to_tsvector('french', coalesce(product_name, '') || ' ' || coalesce(brands, '')))",
        
        # Index composites pour les filtres fréquents
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_nutri_nova_complete ON products (nutriscore_grade, nova_group, completeness) WHERE nutriscore_grade IS NOT NULL",
        
        # Index pour les requêtes de catégories
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_gin ON products USING gin(string_to_array(lower(categories), ','))",
        
        # Index pour les statistiques
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stats_nutrition ON products (energy_100g, fat_100g, proteins_100g) WHERE energy_100g IS NOT NULL",
        
        # Statistiques pour l'optimiseur
        "ANALYZE products"
    ]
    
    with engine.connect() as conn:
        for optimization in optimizations:
            try:
                logger.info(f"Exécution: {optimization[:50]}...")
                conn.execute(text(optimization))
                conn.commit()
                logger.info("✅ Optimisation appliquée")
            except Exception as e:
                logger.warning(f"⚠️ Optimisation échouée: {e}")
    
    logger.info("🎉 Optimisation terminée")

if __name__ == "__main__":
    optimize_database() 