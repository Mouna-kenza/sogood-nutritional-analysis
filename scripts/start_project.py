#!/usr/bin/env python3
"""
Script de démarrage pour SoGood
"""
import subprocess
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    try:
        import fastapi
        import sqlalchemy
        import pandas
        logger.info("✅ Dépendances Python OK")
        return True
    except ImportError as e:
        logger.error(f"❌ Dépendance manquante: {e}")
        return False

def check_database():
    """Vérifie la connexion à la base de données"""
    try:
        from backend.database import check_database_connection
        if check_database_connection():
            logger.info("✅ Base de données connectée")
            return True
        else:
            logger.error("❌ Impossible de se connecter à la base de données")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur base de données: {e}")
        return False

def load_sample_data():
    """Charge un échantillon de données pour tester"""
    try:
        logger.info("📊 Chargement d'un échantillon de données...")
        subprocess.run([
            sys.executable, "scripts/load_data.py", 
            "--max-rows", "1000"
        ], check=True)
        logger.info("✅ Données d'exemple chargées")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur chargement données: {e}")
        return False

def start_api():
    """Démarre l'API FastAPI"""
    try:
        logger.info("🚀 Démarrage de l'API...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt de l'API")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur démarrage API: {e}")

def main():
    """Point d'entrée principal"""
    logger.info("🥗 Démarrage de SoGood - Analyse Nutritionnelle")
    
    # Vérifications préliminaires
    if not check_dependencies():
        logger.error("❌ Vérifiez l'installation des dépendances: pip install -r requirements.txt")
        return 1
    
    if not check_database():
        logger.error("❌ Vérifiez la configuration de la base de données")
        logger.info("💡 Lancez: docker-compose up -d postgres")
        return 1
    
    # Chargement des données si nécessaire
    answer = input("📊 Charger des données d'exemple? (y/N): ")
    if answer.lower() in ['y', 'yes', 'o', 'oui']:
        if not load_sample_data():
            logger.warning("⚠️ Échec du chargement des données, mais on continue...")
    
    # Démarrage de l'API
    start_api()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 