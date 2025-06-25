#!/bin/bash
# Script de démarrage SoGood

echo "🥗 Démarrage de SoGood - Analyse Nutritionnelle"
echo "================================================"

# Vérifier si Python est installé
if ! command -v python &> /dev/null; then
    echo "❌ Python n'est pas installé"
    exit 1
fi

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi

# Test de l'installation
echo "🔍 Test de l'installation..."
python test_setup.py

if [ $? -ne 0 ]; then
    echo "❌ Tests échoués. Vérifiez l'installation."
    exit 1
fi

# Créer le fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cp env.example .env
    echo "✅ Fichier .env créé"
fi

# Démarrer PostgreSQL
echo "🐘 Démarrage de PostgreSQL..."
docker-compose up -d postgres

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente du démarrage de PostgreSQL..."
sleep 10

# Charger un échantillon de données
echo "📊 Chargement d'un échantillon de données..."
python scripts/load_data.py --max-rows 1000 --batch-size 100

# Démarrer l'API
echo "🚀 Démarrage de l'API..."
python backend/main.py 