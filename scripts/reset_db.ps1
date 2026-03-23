# =========================================
# RESET & FRESH LOAD FOR RISK_DB
# Postgres 16 + Docker
# =========================================

$ErrorActionPreference = "Stop"

# -------------------------------------------------
# 1️⃣ Config
# -------------------------------------------------
$containerName = "risk-postgres"
$dbName = "risk_db"
$dbUser = "postgres"

$sqlFile = "database/fresh_all.sql"
$migrationsFolder = "database/migrations"

Write-Host ""
Write-Host "=== RISK DB RESET STARTED ==="
Write-Host ""

# -------------------------------------------------
# 2️⃣ Container running check
# -------------------------------------------------
Write-Host "Checking Docker container..."

$running = docker ps --format "{{.Names}}" | Select-String $containerName

if (-not $running) {
    Write-Host "ERROR: Container '$containerName' is not running."
    exit 1
}

Write-Host "Container is running."

# -------------------------------------------------
# 3️⃣ Prepare container database folder
# -------------------------------------------------
Write-Host "Preparing /database directory inside container..."

docker exec $containerName mkdir -p /database

# -------------------------------------------------
# 4️⃣ Copy migrations folder
# -------------------------------------------------
Write-Host "Copying migrations folder into container..."

docker cp $migrationsFolder "${containerName}:/database/"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to copy migrations folder."
    exit 1
}

# -------------------------------------------------
# 5️⃣ Copy fresh_all.sql
# -------------------------------------------------
Write-Host "Copying fresh_all.sql into container..."

docker cp $sqlFile "${containerName}:/fresh_all.sql"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to copy fresh_all.sql."
    exit 1
}

# -------------------------------------------------
# 6️⃣ Execute SQL
# -------------------------------------------------
Write-Host "Executing database reset..."

docker exec -i $containerName `
    psql -U $dbUser -d $dbName -f "/fresh_all.sql"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database setup failed."
    exit 1
}

# -------------------------------------------------
# 7️⃣ Done
# -------------------------------------------------
Write-Host ""
Write-Host "Database reset and fresh load completed successfully!"
Write-Host ""