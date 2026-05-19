param(
    [ValidateSet("start","stop","restart","status","log","update")]
    [string]$Command = "status"
)

$GW_PORT = 18789
$OLLAMA = "C:\Users\denk0\AppData\Local\Programs\Ollama\ollama.exe"
$LOG = "C:\Users\denk0\AppData\Local\Temp\openclaw\openclaw-$(Get-Date -Format 'yyyy-MM-dd').log"

switch ($Command) {
    "start" {
        Write-Host "Starting Ollama..." -ForegroundColor Cyan
        $env:OLLAMA_HOST = "127.0.0.1"
        $proc = Get-Process ollama -ErrorAction SilentlyContinue
        if (-not $proc) {
            Start-Process -WindowStyle Hidden -FilePath $OLLAMA -ArgumentList "serve"
            Start-Sleep -Seconds 3
        }
        Write-Host "Starting OpenClaw Gateway..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoExit","-Command","openclaw gateway run --port $GW_PORT --force" -WindowStyle Minimized
        Start-Sleep -Seconds 8
        openclaw gateway health
    }
    "stop" {
        Write-Host "Stopping OpenClaw Gateway..." -ForegroundColor Yellow
        Get-Process -Name "powershell" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "openclaw gateway" } | Stop-Process -Force
        Write-Host "Stopping Ollama..." -ForegroundColor Yellow
        Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
        Get-Process "ollama app" -ErrorAction SilentlyContinue | Stop-Process -Force
        Write-Host "Stopped." -ForegroundColor Green
    }
    "restart" {
        & $PSCommandPath stop
        Start-Sleep -Seconds 2
        & $PSCommandPath start
    }
    "status" {
        Write-Host "=== OpenClaw Status ===" -ForegroundColor Cyan
        openclaw status 2>&1
        Write-Host "`n=== Ports ===" -ForegroundColor Cyan
        netstat -ano | Select-String ":18789|:18791|:11434"
    }
    "log" {
        if (Test-Path $LOG) {
            Get-Content -Tail 30 $LOG
        } else {
            Write-Host "Log not found: $LOG" -ForegroundColor Red
        }
    }
    "update" {
        Write-Host "Updating OpenClaw..." -ForegroundColor Cyan
        npm update -g openclaw 2>&1
        Write-Host "Updating OpenCode config..." -ForegroundColor Cyan
        openclaw models scan
    }
}
