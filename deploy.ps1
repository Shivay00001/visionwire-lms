# VisionWire LMS Complete Deployment Script
param(
    [switch]$Dev = $false,
    [switch]$Prod = $false,
    [switch]$Docker = $false,
    [switch]$BackendOnly = $false,
    [switch]$FrontendOnly = $false
)

$ErrorActionPreference = "Continue"
$LMSDir = $PSScriptRoot

# Color functions
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Error-Custom { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ $msg" -ForegroundColor Cyan }
function Write-Warning-Custom { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   VisionWire LMS                       ║" -ForegroundColor Cyan
Write-Host "║   Learning Management System           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Docker deployment
if ($Docker) {
    Write-Info "Docker deployment..."
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error-Custom "Docker not found. Install Docker Desktop"
        exit 1
    }
    
    $dockerComposePath = Join-Path $LMSDir "docker\docker-compose.yml"
    if (-not (Test-Path $dockerComposePath)) {
        $dockerComposePath = Join-Path $LMSDir "docker-compose.yml"
    }
    
    if (Test-Path $dockerComposePath) {
        Write-Info "Starting Docker containers..."
        cd $LMSDir
        docker-compose -f $dockerComposePath up -d --build
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker containers started"
            Write-Info "Backend: http://localhost:8007"
            Write-Info "Frontend: http://localhost:3007"
        }
        else {
            Write-Error-Custom "Docker deployment failed"
            exit 1
        }
    }
    else {
        Write-Error-Custom "docker-compose.yml not found"
        exit 1
    }
    exit 0
}

# Standard deployment
$jobs = @()

# Start backend
if (-not $FrontendOnly) {
    Write-Info "Starting backend..."
    
    $backendScript = Join-Path $LMSDir "backend\deploy-backend.ps1"
    if (-not (Test-Path $backendScript)) {
        $backendScript = Join-Path $LMSDir "deploy-backend.ps1"
    }
    
    if (Test-Path $backendScript) {
        $args = @()
        if ($Dev) { $args += "-Dev" }
        if ($Prod) { $args += "-Prod" }
        
        $backendJob = Start-Job -ScriptBlock {
            param($script, $args)
            & $script @args
        } -ArgumentList $backendScript, $args
        
        $jobs += $backendJob
        Write-Success "Backend starting..."
        
        # Wait for backend to be ready
        Start-Sleep -Seconds 3
    }
    else {
        Write-Error-Custom "Backend deployment script not found"
    }
}

# Start frontend
if (-not $BackendOnly) {
    Write-Info "Starting frontend..."
    
    $frontendScript = Join-Path $LMSDir "frontend\deploy-frontend.ps1"
    if (-not (Test-Path $frontendScript)) {
        $frontendScript = Join-Path $LMSDir "deploy-frontend.ps1"
    }
    
    if (Test-Path $frontendScript) {
        $args = @()
        if ($Dev) { $args += "-Dev" }
        if ($Prod) { $args += "-Prod" }
        
        $frontendJob = Start-Job -ScriptBlock {
            param($script, $args)
            & $script @args
        } -ArgumentList $frontendScript, $args
        
        $jobs += $frontendJob
        Write-Success "Frontend starting..."
    }
    else {
        Write-Error-Custom "Frontend deployment script not found"
    }
}

# Display status
Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Success "VisionWire LMS Deployment Complete"
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host ""

if (-not $FrontendOnly) {
    Write-Info "Backend API: http://localhost:8007"
    Write-Info "API Docs: http://localhost:8007/docs"
}

if (-not $BackendOnly) {
    Write-Info "Frontend UI: http://localhost:3007"
}

Write-Host ""
Write-Warning-Custom "Press Ctrl+C to stop all services"
Write-Host ""

# Wait for jobs
if ($jobs.Count -gt 0) {
    Wait-Job $jobs | Out-Null
    Receive-Job $jobs
}
