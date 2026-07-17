# PowerShell script to create test users on Render
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AgriVision - Create Render Test Users" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test backend first
Write-Host "[1/3] Testing Render backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "https://agrivision2.onrender.com/health" -TimeoutSec 10
    Write-Host "✓ Backend is online" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend is not responding" -ForegroundColor Red
    Write-Host "  Please wait for Render deployment to complete" -ForegroundColor Yellow
    Write-Host "  Check: https://dashboard.render.com" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[2/3] Creating test users..." -ForegroundColor Yellow

$users = @(
    @{
        email = "farmer@test.com"
        password = "password123"
        full_name = "Test Farmer"
        role = "farmer"
    },
    @{
        email = "admin@test.com"
        password = "password123"
        full_name = "Test Admin"
        role = "admin"
    },
    @{
        email = "expert@test.com"
        password = "password123"
        full_name = "Test Expert"
        role = "expert"
    }
)

$successCount = 0
$errorCount = 0

foreach ($user in $users) {
    $body = $user | ConvertTo-Json
    try {
        $result = Invoke-RestMethod -Uri "https://agrivision2.onrender.com/api/v1/auth/register" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body `
            -TimeoutSec 15
        
        Write-Host "  ✓ Created: $($user.email)" -ForegroundColor Green
        $successCount++
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $errorMessage = $_.ErrorDetails.Message
        
        if ($statusCode -eq 400 -and $errorMessage -like "*already registered*") {
            Write-Host "  ◉ Exists: $($user.email)" -ForegroundColor Yellow
            $successCount++
        } else {
            Write-Host "  ✗ Failed: $($user.email) (HTTP $statusCode)" -ForegroundColor Red
            $errorCount++
        }
    }
}

Write-Host ""
Write-Host "[3/3] Testing login..." -ForegroundColor Yellow

$loginBody = @{
    email = "farmer@test.com"
    password = "password123"
} | ConvertTo-Json

try {
    $loginResult = Invoke-RestMethod -Uri "https://agrivision2.onrender.com/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -TimeoutSec 15
    
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  Token: $($loginResult.access_token.Substring(0, 30))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Users created/verified: $successCount" -ForegroundColor $(if ($successCount -eq 3) { "Green" } else { "Yellow" })
Write-Host "  Errors: $errorCount" -ForegroundColor $(if ($errorCount -eq 0) { "Green" } else { "Red" })
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($successCount -eq 3 -and $errorCount -eq 0) {
    Write-Host "✓ All Done! You can now login at:" -ForegroundColor Green
    Write-Host "  https://agri-vision1.vercel.app/auth/login" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test Accounts:" -ForegroundColor Yellow
    Write-Host "  farmer@test.com / password123" -ForegroundColor White
    Write-Host "  admin@test.com / password123" -ForegroundColor White
    Write-Host "  expert@test.com / password123" -ForegroundColor White
} else {
    Write-Host "⚠ Some users could not be created" -ForegroundColor Yellow
    Write-Host "  This might mean:" -ForegroundColor Yellow
    Write-Host "  1. Render is still deploying (wait 2 minutes)" -ForegroundColor Yellow
    Write-Host "  2. Backend has an error (check Render logs)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Try running this script again in 2 minutes" -ForegroundColor Yellow
}

Write-Host ""
