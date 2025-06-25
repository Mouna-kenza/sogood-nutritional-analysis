# Script de démarrage SoGood pour Windows PowerShell

Write-Host "🥗 Démarrage de SoGood - Analyse Nutritionnelle" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Vérifier si Python est installé
try {
    python --version | Out-Null
    Write-Host "✅ Python trouvé" -ForegroundColor Green
} catch {
    Write-Host "❌ Python n'est pas installé" -ForegroundColor Red
    exit 1
}

# Vérifier si Docker est installé
try {
    docker --version | Out-Null
    Write-Host "✅ Docker trouvé" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker n'est pas installé" -ForegroundColor Red
    exit 1
}

# Test de l'installation
Write-Host "🔍 Test de l'installation..." -ForegroundColor Yellow
python test_setup.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests échoués. Vérifiez l'installation." -ForegroundColor Red
    exit 1
}

# Créer le fichier .env s'il n'existe pas
if (-not (Test-Path ".env")) {
    Write-Host "📝 Création du fichier .env..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host "✅ Fichier .env créé" -ForegroundColor Green
}

# Démarrer PostgreSQL
Write-Host "🐘 Démarrage de PostgreSQL..." -ForegroundColor Yellow
docker-compose up -d postgres

# Attendre que PostgreSQL soit prêt
Write-Host "⏳ Attente du démarrage de PostgreSQL..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Charger un échantillon de données
Write-Host "📊 Chargement d'un échantillon de données..." -ForegroundColor Yellow
python scripts/load_data.py --max-rows 1000 --batch-size 100

# Démarrer l'API
Write-Host "🚀 Démarrage de l'API..." -ForegroundColor Yellow
python backend/main.py 