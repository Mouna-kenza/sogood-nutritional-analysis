from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging
import uvicorn

from backend.config import settings
from backend.database import get_db, check_database_connection, create_tables
from backend.controllers.product_controller import router as product_router
from backend.models.product import Product

# Configuration des logs
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Configuration CORS pour le frontend Flask
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000"],  # Frontend Flask
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(product_router, prefix="/api/v1/products", tags=["products"])

@app.on_event("startup")
async def startup_event():
    """Événements au démarrage de l'application"""
    logger.info(f"🚀 Démarrage de {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"🔧 Environnement: {settings.ENVIRONMENT}")
    
    # Vérifier la connexion à la base de données
    if not check_database_connection():
        logger.error("❌ Impossible de se connecter à la base de données")
        raise RuntimeError("Connexion base de données échouée")
    
    # Créer les tables si nécessaire
    try:
        create_tables()
        logger.info("✅ Tables vérifiées/créées")
    except Exception as e:
        logger.error(f"❌ Erreur création tables: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Événements à l'arrêt de l'application"""
    logger.info("🛑 Arrêt de l'application SoGood")

@app.get("/")
async def root():
    """Point d'entrée racine de l'API"""
    return {
        "message": f"🥗 {settings.APP_NAME} - API d'analyse nutritionnelle",
        "version": settings.APP_VERSION,
        "status": "active",
        "endpoints": {
            "products": "/api/v1/products",
            "search": "/api/v1/products/search",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Vérification de l'état de santé de l'API"""
    try:
        # Test de la base de données
        product_count = db.query(Product).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "products_count": product_count,
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 