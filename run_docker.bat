@echo off
echo =========================================
echo   Synaptix Docker Launcher
echo =========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b
)

echo [1/2] Building and Starting Containers...
echo -----------------------------------------
docker-compose up --build

echo.
echo [STOPPED]
pause
