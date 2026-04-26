@echo off
REM ============================================================
REM  Braille Dome - Construtor v6
REM  Adiciona networkx por seguranca (alguns metodos do trimesh
REM  ainda o podem invocar internamente).
REM ============================================================

echo.
echo ============================================
echo  Braille Dome - Gerar executaveis (v6)
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado.
    pause
    exit /b 1
)

echo [1/5] Python encontrado.
python --version

echo.
echo [2/5] A instalar dependencias...
python -m pip install --upgrade pip
python -m pip install pyinstaller flask waitress numpy trimesh shapely networkx
if errorlevel 1 (
    echo [ERRO] Falhou a instalacao.
    pause
    exit /b 1
)

echo.
echo [3/5] A limpar builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist BrailleDome.spec del BrailleDome.spec
if exist BrailleDome_DEBUG.spec del BrailleDome_DEBUG.spec

echo.
echo [4/5] A construir BrailleDome.exe (normal)...
echo.

python -m PyInstaller ^
    --name BrailleDome ^
    --onefile ^
    --windowed ^
    --add-data "braille_dome.py;." ^
    --add-data "svg_to_stl.py;." ^
    --add-data "app.py;." ^
    --hidden-import=trimesh ^
    --hidden-import=shapely ^
    --hidden-import=networkx ^
    --hidden-import=flask ^
    --hidden-import=waitress ^
    --collect-all=trimesh ^
    --collect-all=waitress ^
    --collect-all=networkx ^
    braille_dome_app.py

if errorlevel 1 (
    echo [ERRO] Falhou a construcao do BrailleDome.exe.
    pause
    exit /b 1
)

echo.
echo [5/5] A construir BrailleDome_DEBUG.exe...
echo.

python -m PyInstaller ^
    --name BrailleDome_DEBUG ^
    --onefile ^
    --console ^
    --add-data "braille_dome.py;." ^
    --add-data "svg_to_stl.py;." ^
    --add-data "app.py;." ^
    --hidden-import=trimesh ^
    --hidden-import=shapely ^
    --hidden-import=networkx ^
    --hidden-import=flask ^
    --hidden-import=waitress ^
    --collect-all=trimesh ^
    --collect-all=waitress ^
    --collect-all=networkx ^
    braille_dome_app.py

if errorlevel 1 (
    echo [ERRO] Falhou a construcao do DEBUG.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  PRONTO!
echo ============================================
echo.
echo  Executaveis em:
echo     dist\BrailleDome.exe
echo     dist\BrailleDome_DEBUG.exe
echo.
pause
