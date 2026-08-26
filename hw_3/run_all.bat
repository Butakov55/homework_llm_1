@echo off
chcp 65001 > nul
echo ============================================================
echo 🚀 Starting Docker + Ollama + Tests Generator
echo ============================================================
echo.

REM Step 1: Запускаем Ollama
echo 📦 Step 1: Starting Ollama...
call scripts\run_ollama.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to start Ollama
    pause
    exit /b 1
)

echo.
echo ============================================================
echo.

REM Step 2: Генерируем тесты
echo 🤖 Step 2: Generating tests with Ollama...
docker-compose run --rm test-generator python scripts/generate_tests.py
if %errorlevel% neq 0 (
    echo ❌ Failed to generate tests
    pause
    exit /b 1
)

echo.
echo ============================================================
echo.

REM Step 3: Запускаем тесты
echo 🧪 Step 3: Running tests...
docker-compose run --rm test-generator pytest tests/ -v --tb=short --html=report.html

echo.
echo ============================================================
echo ✅ All steps completed successfully!
echo 📊 Test report saved to report.html
echo ============================================================
pause