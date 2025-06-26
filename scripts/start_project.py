#!/usr/bin/env python3
"""
Script de démarrage du projet SoGood
Vérifie l'installation et lance les services
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 10):
        logger.error("❌ Python 3.10+ requis")
        return False
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_docker():
    """Vérifie que Docker est installé"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        logger.info(f"✅ Docker: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ Docker non trouvé")
        return False

def check_docker_compose():
    """Vérifie que Docker Compose est installé"""
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, check=True)
        logger.info(f"✅ Docker Compose: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ Docker Compose non trouvé")
        return False

def check_env_file():
    """Vérifie et crée le fichier .env si nécessaire"""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            import shutil
            shutil.copy('env.example', '.env')
            logger.info("✅ Fichier .env créé depuis env.example")
        else:
            logger.error("❌ Fichier env.example non trouvé")
            return False
    else:
        logger.info("✅ Fichier .env existe")
    return True

def check_requirements():
    """Vérifie les dépendances Python"""
    dependencies = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('cassandra-driver', 'cassandra'),
        ('cqlengine', 'cqlengine'),
        ('pydantic', 'pydantic'),
        ('pandas', 'pandas')
    ]
    
    missing = []
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            logger.info(f"✅ {package_name}")
        except ImportError:
            missing.append(package_name)
            logger.error(f"❌ {package_name} manquant")
    
    if missing:
        logger.info("💡 Lancez: pip install -r requirements.txt")
        return False
    
    logger.info("✅ Toutes les dépendances Python sont installées")
    return True

def main():
    """Fonction principale"""
    logger.info("🔍 Vérification de l'installation SoGood")
    logger.info("=" * 50)
    
    checks = [
        check_python_version(),
        check_docker(),
        check_docker_compose(),
        check_env_file(),
        check_requirements()
    ]
    
    if all(checks):
        logger.info("🎉 Installation OK !")
        logger.info("")
        logger.info("🚀 Pour démarrer le projet:")
        logger.info("   Linux/Mac: ./start.sh")
        logger.info("   Windows: .\\start.ps1")
        logger.info("")
        logger.info("💡 Ou manuellement:")
        logger.info("   1. docker-compose up -d cassandra")
        logger.info("   2. python scripts/init_cassandra.py")
        logger.info("   3. docker-compose up -d api")
        logger.info("   4. cd frontend/web_app && python app.py")
        return 0
    else:
        logger.error("❌ Installation incomplète")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 