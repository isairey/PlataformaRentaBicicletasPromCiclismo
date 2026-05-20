# Arranca MySQL (Docker), espera a que acepte sesiones reales y ejecuta migraciones + Flask en el host.
# Uso (desde esta carpeta):  .\run-local.ps1
# Requisitos: Docker Desktop, Python con dependencias del map, RabbitMQ en 5672 si pruebas RPC.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Levantando MySQL (docker compose)..." -ForegroundColor Cyan
docker compose up -d mysql
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Solo comprobar el puerto TCP deja pasar migraciones demasiado pronto (MySQL aun inicializando -> error 2013).
Write-Host "Esperando a que MySQL responda dentro del contenedor (hasta ~120s la primera vez)..." -ForegroundColor Cyan
$deadline = (Get-Date).AddSeconds(120)
$ready = $false
# Contrasena por env (evita aviso en stderr) y SilentlyContinue: stderr de mysqladmin no debe disparar error con $ErrorActionPreference Stop.
$prevEap = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
while ((Get-Date) -lt $deadline) {
    docker compose exec -T -e MYSQL_PWD=rootpass mysql mysqladmin ping -h localhost -uroot *> $null
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}
$ErrorActionPreference = $prevEap
if (-not $ready) {
    Write-Host "MySQL no respondio a tiempo. Revisa: docker compose ps / docker compose logs mysql" -ForegroundColor Red
    exit 1
}

# Margen extra para que el servidor complete el handshake tras el primer ping (evita 2013 en la primera query del cliente).
Start-Sleep -Seconds 3

$env:FLASK_APP = "main.py"
$env:PYTHONPATH = $PSScriptRoot
$env:DATABASE_URL = "mysql+pymysql://map_user:map_pass@127.0.0.1:3308/geo_db"
$env:RABBITMQ_URL = "amqp://guest:guest@127.0.0.1:5672/"
$env:ENABLE_RABBIT_CONSUMERS = "1"
if (-not $env:FLASK_SECRET_KEY) { $env:FLASK_SECRET_KEY = "dev-local" }

Write-Host "Ejecutando migraciones..." -ForegroundColor Cyan
$migrateOk = $false
for ($i = 1; $i -le 5; $i++) {
    python -m flask db upgrade
    if ($LASTEXITCODE -eq 0) {
        $migrateOk = $true
        break
    }
    Write-Host "Migracion fallo (intento $i/5). Reintentando en 4s..." -ForegroundColor Yellow
    Start-Sleep -Seconds 4
}
if (-not $migrateOk) {
    Write-Host "flask db upgrade fallo tras reintentos. Prueba: docker compose logs mysql" -ForegroundColor Red
    exit 1
}

Write-Host "Iniciando API en http://127.0.0.1:8081 (Ctrl+C para salir)" -ForegroundColor Green
python -m flask run --host=0.0.0.0 --port=8081
