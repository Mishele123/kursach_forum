$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8000"

function Test-Endpoint($url, $description) {
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        Write-Host "$description : $($response.StatusCode)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "$description : FAILED ($($_.Exception.Message))" -ForegroundColor Red
        return $false
    }
}

Write-Host "Базовая проверка"
Test-Endpoint "$baseUrl/docs" "API /docs"

Write-Host "`Отказоустойчивость: Redis недоступен"
docker compose stop redis
Start-Sleep -Seconds 3
Test-Endpoint "$baseUrl/posts?limit=1" "GET /posts (без Redis)"
try { Invoke-WebRequest -Uri "$baseUrl/auth/login" -Method POST -Body '{"email":"alice@example.com","password":"TestPassword123"}' -ContentType "application/json" -UseBasicParsing -TimeoutSec 5 } catch { Write-Host "/auth/login корректно вернул ошибку: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow }
docker compose start redis
Start-Sleep -Seconds 5

Write-Host "Отказоустойчивость: PostgreSQL недоступен"
docker compose stop postgres
Start-Sleep -Seconds 3
try { Invoke-WebRequest -Uri "$baseUrl/posts?limit=1" -UseBasicParsing -TimeoutSec 5 } catch { Write-Host "/posts корректно вернул ошибку: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow }
docker compose start postgres
Start-Sleep -Seconds 10

Write-Host "Восстановление"
Test-Endpoint "$baseUrl/docs" "API /docs после восстановления"
