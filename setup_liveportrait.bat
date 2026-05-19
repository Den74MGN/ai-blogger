@echo off
chcp 65001 >nul
title Установка LivePortrait

echo ============================================
echo  Установка LivePortrait для AI IT-Блогера
echo ============================================
echo.

cd /d "%~dp0"

echo [1/4] Клонирую репозиторий LivePortrait...
if exist "LivePortrait" (
    echo LivePortrait уже существует, обновляю...
    cd LivePortrait
    git pull
    cd ..
) else (
    git clone https://github.com/KlingAIResearch/LivePortrait.git
)

echo.
echo [2/4] Устанавливаю зависимости...
cd LivePortrait
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

echo.
echo [3/4] Скачиваю веса модели...
pip install -U "huggingface_hub[cli]"
huggingface-cli download KlingTeam/LivePortrait --local-dir pretrained_weights --exclude "*.git*" README.md

echo.
echo [4/4] Создаю driving видео из исходных материалов...

set "SOURCE_DIR=..\avatar\source"
set "DRIVING_DIR=..\avatar\driving"

if not exist "%DRIVING_DIR%" mkdir "%DRIVING_DIR%"

for %%f in ("%SOURCE_DIR%\*.mp4" "%SOURCE_DIR%\*.mov" "%SOURCE_DIR%\*.avi") do (
    copy "%%f" "%DRIVING_DIR%\drive.mp4"
    echo Использую %%f как driving видео
    goto :found_video
)

:found_video
if not exist "%DRIVING_DIR%\drive.mp4" (
    echo Создаю тестовое driving видео...
    ffmpeg -y -f lavfi -i "color=c=blue:s=512x512:d=5:r=30" -c:v libx264 -pix_fmt yuv420p "%DRIVING_DIR%\drive.mp4"
)

echo.
echo ============================================
echo  Установка завершена!
echo ============================================
echo.
echo Запуск: python main.py --once "тема видео"
echo Расписание: python main.py --schedule
pause
