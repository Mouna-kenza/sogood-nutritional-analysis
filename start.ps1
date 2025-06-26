# Script de démarrage pour SoGood (PowerShell)
# Usage: .\start.ps1

Write-Host "🥗 SoGood - Démarrage du projet" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Vérifier que Docker est installé
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker n'est pas installé. Veuillez installer Docker Desktop." -ForegroundColor Red
    exit 1
}

# Vérifier que Docker Compose est installé
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose n'est pas installé." -ForegroundColor Red
    exit 1
}

# Vérifier que le fichier .env existe
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Fichier .env non trouvé. Copie depuis env.example..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host "✅ Fichier .env créé" -ForegroundColor Green
}

# Arrêter les conteneurs existants
Write-Host "🛑 Arrêt des conteneurs existants..." -ForegroundColor Yellow
docker-compose down

# Démarrer Cassandra
Write-Host "🐘 Démarrage de Cassandra..." -ForegroundColor Yellow
docker-compose up -d cassandra

# Attendre que Cassandra soit prêt
Write-Host "⏳ Attente du démarrage de Cassandra..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Vérifier que Cassandra est prêt
Write-Host "🔍 Vérification de Cassandra..." -ForegroundColor Yellow
try {
    docker-compose exec cassandra cqlsh -e "SELECT release_version FROM system.local;" | Out-Null
    Write-Host "✅ Cassandra est prêt" -ForegroundColor Green
} catch {
    Write-Host "❌ Cassandra n'est pas prêt. Attente supplémentaire..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# Initialiser Cassandra
Write-Host "🔧 Initialisation de Cassandra..." -ForegroundColor Yellow
python scripts/init_cassandra.py

# Démarrer l'API
Write-Host "🚀 Démarrage de l'API..." -ForegroundColor Yellow
docker-compose up -d api

# Attendre que l'API soit prête
Write-Host "⏳ Attente du démarrage de l'API..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Vérifier que l'API répond
Write-Host "🔍 Vérification de l'API..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get | Out-Null
    Write-Host "✅ API est prête" -ForegroundColor Green
} catch {
    Write-Host "⚠️  API pas encore prête. Vérifiez les logs avec: docker-compose logs api" -ForegroundColor Yellow
}

# Démarrer le frontend
Write-Host "🌐 Démarrage du frontend..." -ForegroundColor Yellow
Set-Location "frontend/web_app"
Start-Process python -ArgumentList "app.py" -WindowStyle Hidden

# Attendre un peu
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "🎉 SoGood est prêt !" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host "📊 API Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📚 Documentation API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🐘 Cassandra: localhost:9042" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour arrêter: Ctrl+C puis .\stop.ps1" -ForegroundColor Yellow
Write-Host ""

# Attendre l'interruption
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host ""
    Write-Host "🛑 Arrêt..." -ForegroundColor Yellow
    docker-compose down
    exit 0
} 