@echo off
echo Starting Ollama service...

REM Проверяем, запущен ли контейнер
docker ps | findstr ollama > nul
if %errorlevel% equ 0 (
    echo [OK] Ollama already running
) else (
    echo [INFO] Starting Ollama container...
    docker-compose up -d ollama
    echo [INFO] Waiting for Ollama to start...
    timeout /t 15 /nobreak > nul
)

REM Проверяем, загружена ли модель
set MODEL_NAME=codellama:7b-code
echo [INFO] Checking if model %MODEL_NAME% is downloaded...

docker exec ollama ollama list | findstr %MODEL_NAME% > nul
if %errorlevel% equ 0 (
    echo [OK] Model %MODEL_NAME% already downloaded
) else (
    echo [INFO] Downloading model %MODEL_NAME% (this may take several minutes)...
    docker exec ollama ollama pull %MODEL_NAME%
)

echo [OK] Ollama is ready!
echo [INFO] API endpoint: http://localhost:11434
echo [INFO] Model: %MODEL_NAME%