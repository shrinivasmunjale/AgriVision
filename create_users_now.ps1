# Quick script to create users on Render
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Creating Test Users on Render NOW" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$users = @(
    @{email="farmer@test.com";password="password123";full_name="Test Farmer";role="farmer"},
    @{email="admin@test.com";password="password123";full_name="Test Admin";role="admin"},
    @{email="expert@test.com";password="password123";full_name="Test Expert";role="expert"}
)

$success = 0
foreach ($u in $users) {
    $body = $u | ConvertTo-Json
    Write-Host "Creating $($u.email)..." -NoNewline
    try {
        Invoke-RestMethod -Uri "https://agrivision2.onrender.com/api/v1/auth/register" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body `
            -TimeoutSec 20 | Out-Null
        Write-Host " ✓" -ForegroundColor Green
        $success++
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        if ($code -eq 400) {
            Write-Host " ◉ (exists)" -ForegroundColor Yellow
            $success++
        } else {
            Write-Host " ✗ (HTTP $code)" -ForegroundColor Red
        }
    }
}

Write-Host ""
if ($success -ge 3) {
    Write-Host "Testing login..." -NoNewline
    $loginBody = @{email="farmer@test.com";password="password123"} | ConvertTo-Json
    try {
        $result = Invoke-RestMethod -Uri "https://agrivision2.onrender.com/api/v1/auth/login" `
            -Method POST `
            -ContentType "application/json" `
            -Body $loginBody `
            -TimeoutSec 15
        Write-Host " ✓ WORKS!" -ForegroundColor Green
        Write-Host "`n✓ SUCCESS! Login at:" -ForegroundColor Green
        Write-Host "  https://agri-vision1.vercel.app/auth/login" -ForegroundColor Cyan
    } catch {
        Write-Host " ✗ Failed" -ForegroundColor Red
    }
} else {
    Write-Host "⚠ Render may still be deploying. Wait 2 minutes and run again." -ForegroundColor Yellow
}

Write-Host ""
