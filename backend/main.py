from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from backend.controllers.product_controller import router as product_router
from backend.controllers.stats_controller import router as stats_router
from backend.database import check_database_connection, create_tables
from backend.config import settings

# Configuration des logs
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(product_router, prefix="/api/products", tags=["products"])
app.include_router(stats_router, tags=["statistics"])

@app.on_event("startup")
async def startup_event():
    """Événement de démarrage de l'application"""
    logger.info("🚀 Démarrage de l'application SoGood")
    
    # Vérifier la connexion à la base de données
    if not check_database_connection():
        logger.error("❌ Impossible de se connecter à Cassandra")
        raise Exception("Erreur de connexion à la base de données")
    
    # Créer les tables si nécessaire
    try:
        create_tables()
        logger.info("✅ Tables créées avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur création des tables: {e}")
        raise

@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "SoGood API - Analyse nutritionnelle",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    try:
        db_ok = check_database_connection()
        return {
            "status": "healthy" if db_ok else "unhealthy",
            "database": "connected" if db_ok else "disconnected",
            "version": settings.APP_VERSION
        }
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        raise HTTPException(status_code=500, detail="Service indisponible") 