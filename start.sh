#!/bin/bash
# Script de démarrage pour SoGood
# Usage: ./start.sh

set -e

echo "🥗 SoGood - Démarrage du projet"
echo "================================"

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker Desktop."
    exit 1
fi

# Vérifier que Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé."
    exit 1
fi

# Vérifier que le fichier .env existe
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env non trouvé. Copie depuis env.example..."
    cp env.example .env
    echo "✅ Fichier .env créé"
fi

# Arrêter les conteneurs existants
echo "🛑 Arrêt des conteneurs existants..."
docker-compose down

# Démarrer Cassandra
echo "🐘 Démarrage de Cassandra..."
docker-compose up -d cassandra

# Attendre que Cassandra soit prêt
echo "⏳ Attente du démarrage de Cassandra..."
sleep 30

# Vérifier que Cassandra est prêt
echo "🔍 Vérification de Cassandra..."
if docker-compose exec cassandra cqlsh -e "SELECT release_version FROM system.local;" > /dev/null 2>&1; then
    echo "✅ Cassandra est prêt"
else
    echo "❌ Cassandra n'est pas prêt. Attente supplémentaire..."
    sleep 30
fi

# Initialiser Cassandra
echo "🔧 Initialisation de Cassandra..."
python scripts/init_cassandra.py

# Démarrer l'API
echo "🚀 Démarrage de l'API..."
docker-compose up -d api

# Attendre que l'API soit prête
echo "⏳ Attente du démarrage de l'API..."
sleep 10

# Vérifier que l'API répond
echo "🔍 Vérification de l'API..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API est prête"
else
    echo "⚠️  API pas encore prête. Vérifiez les logs avec: docker-compose logs api"
fi

# Démarrer le frontend
echo "🌐 Démarrage du frontend..."
cd frontend/web_app
python app.py &
FRONTEND_PID=$!

# Attendre un peu
sleep 5

echo ""
echo "🎉 SoGood est prêt !"
echo "==================="
echo "📊 API Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:5000"
echo "📚 Documentation API: http://localhost:8000/docs"
echo "🐘 Cassandra: localhost:9042"
echo ""
echo "Pour arrêter: Ctrl+C puis ./stop.sh"
echo ""

# Attendre l'interruption
trap "echo ''; echo '🛑 Arrêt...'; kill $FRONTEND_PID; docker-compose down; exit 0" INT
wait 