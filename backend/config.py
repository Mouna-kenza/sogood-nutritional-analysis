import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

class Settings(BaseSettings):
    """Configuration globale de l'application SoGood"""
    
    # Informations de l'application
    APP_NAME: str = "SoGood API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API d'analyse nutritionnelle et de calcul du Nutri-Score"
    
    # Configuration de l'environnement
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # Configuration de Cassandra
    CASSANDRA_HOSTS: str = os.getenv("CASSANDRA_HOSTS", "localhost")
    CASSANDRA_PORT: int = int(os.getenv("CASSANDRA_PORT", "9042"))
    CASSANDRA_USERNAME: str = os.getenv("CASSANDRA_USERNAME", "cassandra")
    CASSANDRA_PASSWORD: str = os.getenv("CASSANDRA_PASSWORD", "cassandra")
    CASSANDRA_KEYSPACE: str = os.getenv("CASSANDRA_KEYSPACE", "sogood")
    CASSANDRA_DATACENTER: str = os.getenv("CASSANDRA_DATACENTER", "datacenter1")
    
    # Configuration du serveur
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))  
    
    # Configuration des données OpenFoodFacts
    OPENFOODFACTS_URL: str = "https://www.data.gouv.fr/fr/datasets/r/164c9e57-32a7-4f5b-8891-26af10f91072"
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    
    # Configuration ML
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "data/models/nutriscore_model.joblib")
    
    # Configuration des logs
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/sogood.log")
    
    # Configuration de pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Instance globale des settings 
settings = Settings() 