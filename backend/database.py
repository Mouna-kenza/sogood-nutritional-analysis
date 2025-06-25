from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import logging
from backend.config import settings

# Configuration de l'engine PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=20,
    max_overflow=0,
    echo=settings.DEBUG
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Métadonnées pour les migrations
metadata = MetaData()

def get_db() -> Session:
    """
    Générateur de session de base de données pour les dépendances FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    """
    Context manager pour les sessions de base de données
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Erreur base de données: {e}")
        raise
    finally:
        db.close()

def create_tables():
    """
    Crée toutes les tables dans la base de données
    """
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("✅ Tables créées avec succès")
    except Exception as e:
        logging.error(f"❌ Erreur création des tables: {e}")
        raise

def check_database_connection() -> bool:
    """
    Vérifie la connexion à la base de données
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logging.info("✅ Connexion à la base de données réussie")
        return True
    except Exception as e:
        logging.error(f"❌ Erreur connexion base de données: {e}")
        return False 