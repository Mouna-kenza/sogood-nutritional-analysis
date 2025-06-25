#!/usr/bin/env python3
"""
Script de démarrage du frontend SoGood
Démarre le frontend Flask qui se connecte à l'API backend
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_backend_status():
    """Vérifie si l'API backend est accessible"""
    try:
        response = requests.get("http://localhost:8000/api/v1/products/stats/database", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 Démarrage du Frontend SoGood")
    print("=" * 50)
    
    # Vérifier que le backend est démarré
    print("🔍 Vérification de l'API backend...")
    if not check_backend_status():
        print("❌ L'API backend n'est pas accessible sur http://localhost:8000")
        print("💡 Assurez-vous que le backend est démarré avec: docker-compose up backend")
        print("   ou avec: python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
        return 1
    
    print("✅ API backend accessible")
    
    # Changer vers le dossier frontend
    frontend_dir = Path("frontend/web_app")
    if not frontend_dir.exists():
        print(f"❌ Dossier frontend non trouvé: {frontend_dir}")
        return 1
    
    print(f"📁 Dossier frontend: {frontend_dir.absolute()}")
    
    # Installer les dépendances si nécessaire
    print("📦 Vérification des dépendances...")
    try:
        import flask
        import requests
        print("✅ Dépendances Flask et requests disponibles")
    except ImportError:
        print("📦 Installation des dépendances...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "requests"], check=True)
    
    # Démarrer le frontend
    print("🌐 Démarrage du frontend Flask...")
    print("📍 URL: http://localhost:5000")
    print("🔗 API Backend: http://localhost:8000")
    print("=" * 50)
    
    try:
        # Changer vers le dossier frontend et démarrer Flask
        subprocess.run([
            sys.executable, "app.py"
        ], cwd=frontend_dir, check=True)
    except KeyboardInterrupt:
        print("\n👋 Arrêt du frontend")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 