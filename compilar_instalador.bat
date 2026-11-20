@echo off
setlocal EnableExtensions
REM ====================================================================
REM   Accion - compilar el programa y armar el instalador (Inno Setup)
REM ====================================================================
REM   Pon este archivo en la carpeta del programa, junto a:
REM     accion.py, recursos_instalador.py, licencias_terceros.py,
REM     datos_ejemplo.py, preparar_ia.py, instalador_accion.iss, EULA_Accion.rtf,
REM     la carpeta licencias y es_palabras.txt.gz (el diccionario del corrector, RLA-ES)
REM   (D:\experimentos con ia\software guion)
REM   Si el diccionario esta en otra parte, cambia la linea DICCIONARIO=
REM   un poco mas abajo.
REM
REM   Doble clic y listo. Hace todo esto:
REM     1. Busca Python (3.10 o mas nuevo; mejor 3.12 o mas).
REM     2. Prepara un entorno aparte (.venv_compilar) con PySide6 y
REM        PyInstaller, para no mezclar con otras librerias del
REM        computador. La primera vez baja unos 300 MB (necesita
REM        internet); las siguientes veces funciona sin internet.
REM     3. Revisa que accion.py no tenga errores.
REM     4. Dibuja el icono y las imagenes del instalador.
REM     5. Arma el programa con PyInstaller en compilacion\dist\Accion
REM        (esa carpeta ya funciona sola: Accion.exe), le saca lo que no
REM        usa (teclado virtual GPL y FFmpeg) y le pone el diccionario,
REM        LICENSE.txt y la carpeta "Licencias de terceros".
REM     6. Arma el instalador con Inno Setup (6 o 7):
REM        instalador\Instalar_Accion_<version>.exe
REM     7. Con IA=si (abajo), arma ademas el instalador con la IA del Asesor
REM        adentro (Ollama y un modelo): Instalar_Accion_<version>_con_IA.exe
REM        La primera vez baja Ollama (1,6 GB) y el modelo (1 a 7 GB); despues
REM        los toma de compilacion\ia_cache sin volver a bajarlos.
REM
REM   Opciones (en una ventana de comandos, despues del nombre):
REM     compilar_instalador.bat actualizar   baja las versiones nuevas de las librerias
REM     compilar_instalador.bat limpio       rehace el entorno .venv_compilar desde cero
REM     compilar_instalador.bat consola      el programa abre con una consola (para ver errores)
REM     compilar_instalador.bat instalador   solo arma el instalador, con el programa que ya
REM                                          esta en compilacion\dist\Accion (sin volver a compilar)
REM ====================================================================

title Accion - compilar el programa y armar el instalador
echo.
echo  ===  Accion: compilar el programa y armar el instalador  ===
echo.

REM --- La carpeta del programa ---
set "CARPETA=%~dp0"
if not exist "%CARPETA%accion.py" set "CARPETA=D:\experimentos con ia\software guion\"
if exist "%CARPETA%accion.py" goto :carpeta_lista
echo  No encuentro accion.py.
echo  Pon este .bat en la carpeta del programa, donde esta accion.py.
goto :error
:carpeta_lista
cd /d "%CARPETA%"
echo  Carpeta: %CARPETA%

REM --- El diccionario del corrector ortografico (es_palabras.txt.gz) ---
REM     (si lo mueves, cambia esta linea; si no esta ahi, se busca junto a
REM      accion.py y en las carpetas diccionario y sistema)
set "DICCIONARIO=D:\experimentos con ia\software guion\es_palabras.txt.gz"

REM --- La IA del Asesor dentro del instalador ---
REM   IA=si          arma tambien Instalar_Accion_<version>_con_IA.exe (IA=no: solo el normal)
REM   IA_MODELO      el modelo que va adentro: qwen3.5:2b (2,7 GB, para computadores de 8 GB
REM                  de memoria; recomendado), qwen3.5:0.8b (1 GB, para los mas modestos) o
REM                  qwen3.5:4b (3,4 GB, para 16 GB). Varios, separados por espacio.
REM   IA_NVIDIA=si   incluye las bibliotecas CUDA de NVIDIA (1,5 GB mas; el instalador va en
REM                  partes: .exe + .bin). Con "no", la IA parte con el procesador y, si el
REM                  computador tiene una NVIDIA que sirve, Accion baja despues solo la parte
REM                  para ella (desde la 1.7.4; unos 1 GB, en segundo plano).
REM   OLLAMA_ZIP     ollama-windows-amd64.zip, si ya lo bajaste (si no, se baja solo)
set "IA=si"
set "IA_MODELO=qwen3.5:2b"
set "IA_NVIDIA=no"
set "OLLAMA_ZIP=D:\experimentos con ia\software guion\ollama-windows-amd64.zip"

REM --- El entorno de Python para compilar ---
set "VENV=%CARPETA%.venv_compilar"
set "VPY=%VENV%\Scripts\python.exe"

REM --- Opciones ---
set "LIMPIO=0"
set "CONSOLA=0"
set "ACTUALIZAR=0"
set "SOLO_INSTALADOR=0"
for %%A in (%*) do (
  if /i "%%~A"=="limpio" set "LIMPIO=1"
  if /i "%%~A"=="consola" set "CONSOLA=1"
  if /i "%%~A"=="actualizar" set "ACTUALIZAR=1"
  if /i "%%~A"=="instalador" set "SOLO_INSTALADOR=1"
)

REM --- Lo que tiene que estar junto a accion.py ---
set "FALTAN=0"
for %%F in (recursos_instalador.py licencias_terceros.py datos_ejemplo.py preparar_ia.py instalador_accion.iss EULA_Accion.rtf licencias\LGPL-3.0.txt licencias\GPL-3.0.txt licencias\LGPL-2.1.txt) do (
  if not exist "%%F" (
    echo  Falta el archivo %%F
    set "FALTAN=1"
  )
)
if "%FALTAN%"=="0" goto :archivos_listos
echo.
echo  Copia esos archivos (vienen en el paquete del instalador) en:
echo      %CARPETA%
echo  junto a accion.py y a este .bat, y vuelve a intentar.
goto :error
:archivos_listos

REM --- Solo el instalador (con el programa ya compilado) ---
if "%SOLO_INSTALADOR%"=="0" goto :compilar_todo
if not exist "compilacion\dist\Accion\Accion.exe" goto :error_sin_programa
if not exist "compilacion\version.txt" goto :error_sin_programa
set "VER="
set /p VER=<"compilacion\version.txt"
if not defined VER goto :error_version
echo  Solo el instalador, con el programa ya compilado (version %VER%).
call :poner_diccionario
if errorlevel 2 goto :error_diccionario_antiguo
if errorlevel 1 goto :error_diccionario
if not exist "%VPY%" goto :error_sin_entorno
"%VPY%" "licencias_terceros.py"
if errorlevel 1 goto :error
echo  Diccionario: %DICC%
echo  %DICC_TIPO%
goto :inno
:compilar_todo

REM --- 1. Python ---
echo.
echo  [1/6] Buscando Python...
set "PYBASE="
call :probar_python py -3
if not defined PYBASE call :probar_python py
if not defined PYBASE call :probar_python python
if defined PYBASE goto :python_listo
echo  No encontre Python 3.10 o mas nuevo.
echo  Instalalo desde https://www.python.org/downloads/ y vuelve a intentar.
goto :error
:python_listo
for /f "delims=" %%V in ('%PYBASE% -c "import sys; print(sys.version.split()[0])"') do echo        Python %%V

REM --- 2. El entorno para compilar ---
echo.
echo  [2/6] Preparando el entorno para compilar (.venv_compilar)...
if "%LIMPIO%"=="1" if exist "%VENV%" rmdir /s /q "%VENV%"
if not exist "%VPY%" goto :crear_venv
"%VPY%" -c "import sys" >nul 2>&1
if errorlevel 1 rmdir /s /q "%VENV%"
:crear_venv
if exist "%VPY%" goto :venv_listo
%PYBASE% -m venv "%VENV%"
if errorlevel 1 goto :error_venv
set "ACTUALIZAR=1"
:venv_listo
"%VPY%" -c "import PySide6, PyInstaller" >nul 2>&1
if errorlevel 1 set "ACTUALIZAR=1"
if "%ACTUALIZAR%"=="0" goto :librerias_listas
echo        Instalando PySide6 y PyInstaller (la primera vez tarda unos minutos)...
"%VPY%" -m pip install --disable-pip-version-check --quiet --upgrade pip
"%VPY%" -m pip install --disable-pip-version-check --upgrade PySide6 pyinstaller
if errorlevel 1 goto :error_pip
for %%P in (python-docx openpyxl pypdf) do (
  "%VPY%" -m pip install --disable-pip-version-check --quiet --upgrade %%P >nul 2>&1
  if errorlevel 1 echo        [aviso] no se pudo instalar %%P: esa funcion quedara desactivada.
)
:librerias_listas
REM pycrdt: la colaboracion en red (se revisa siempre, aunque el entorno ya exista)
"%VPY%" -c "import pycrdt" >nul 2>&1
if not errorlevel 1 goto :pycrdt_listo
echo        Instalando pycrdt, para la colaboracion en red...
"%VPY%" -m pip install --disable-pip-version-check --quiet "pycrdt>=0.12,<0.15" >nul 2>&1
if not errorlevel 1 goto :pycrdt_listo
"%VPY%" -m pip install --disable-pip-version-check --quiet pycrdt >nul 2>&1
if errorlevel 1 echo        [aviso] no se pudo instalar pycrdt: la colaboracion en red quedara desactivada.
:pycrdt_listo
for /f "tokens=1,2" %%A in ('call "%VPY%" -c "import PySide6, PyInstaller; print(PySide6.__version__, PyInstaller.__version__)"') do echo        PySide6 %%A - PyInstaller %%B

REM --- 3. Revisar accion.py ---
echo.
echo  [3/6] Revisando accion.py...
"%VPY%" -c "import ast; ast.parse(open('accion.py', encoding='utf-8').read())"
if errorlevel 1 goto :error_codigo

REM --- 4. Icono, imagenes y version ---
echo.
echo  [4/6] Icono, imagenes del instalador y version...
"%VPY%" "recursos_instalador.py"
if errorlevel 1 goto :error
set "VER="
set /p VER=<"compilacion\version.txt"
if not defined VER goto :error_version
set "ICONO="
if exist "compilacion\accion.ico" set ICONO=--icon "%CARPETA%compilacion\accion.ico"
call :buscar_diccionario
if errorlevel 2 goto :error_diccionario_antiguo
if errorlevel 1 goto :error_diccionario
echo        Diccionario: %DICC%
echo        %DICC_TIPO%
set "VENTANA=--windowed"
if "%CONSOLA%"=="1" set "VENTANA=--console"

REM --- 5. PyInstaller ---
echo.
echo  [5/6] Armando Accion %VER% con PyInstaller (unos minutos)...
"%VPY%" -m PyInstaller --noconfirm --clean --onedir %VENTANA% --noupx ^
  --name Accion ^
  %ICONO% ^
  --version-file "%CARPETA%compilacion\version_info.txt" ^
  --distpath "%CARPETA%compilacion\dist" ^
  --workpath "%CARPETA%compilacion\build" ^
  --specpath "%CARPETA%compilacion" ^
  --exclude-module tkinter ^
  --exclude-module numpy ^
  --hidden-import PySide6.QtNetwork ^
  --collect-submodules pycrdt ^
  --log-level WARN ^
  "%CARPETA%accion.py"
if errorlevel 1 goto :error_pyinstaller
if not exist "compilacion\dist\Accion\Accion.exe" goto :error_pyinstaller
call :poner_diccionario
if errorlevel 2 goto :error_diccionario_antiguo
if errorlevel 1 goto :error_diccionario
"%VPY%" "licencias_terceros.py"
if errorlevel 1 goto :error
echo        Listo: compilacion\dist\Accion\Accion.exe, con el diccionario en sistema

REM --- 6. Inno Setup ---
:inno
echo.
echo  [6/6] Armando el instalador con Inno Setup...
REM (los cinco guiones de ejemplo: se rehacen con esta version del programa; si algo
REM  falla, van los que traia el paquete)
if exist "guiones_ejemplo.py" "%VPY%" "guiones_ejemplo.py"
if errorlevel 1 echo        [aviso] No se pudieron rehacer los guiones de ejemplo: van los del paquete.
REM (los guiones de ejemplo, con correos y telefonos ficticios)
if exist "guiones de ejemplo\*.accion" "%VPY%" "datos_ejemplo.py"
set "ISCC="
for %%I in ("%ProgramFiles%\Inno Setup 7\ISCC.exe" "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" "%LocalAppData%\Programs\Inno Setup 7\ISCC.exe" "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" "%ProgramFiles%\Inno Setup 6\ISCC.exe" "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe") do (
  if not defined ISCC if exist "%%~I" set "ISCC=%%~I"
)
if not defined ISCC for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do if not defined ISCC set "ISCC=%%I"
for %%K in ("HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 7_is1" "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 7_is1" "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1" "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1" "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1") do (
  if not defined ISCC for /f "tokens=2,*" %%A in ('reg query %%K /v InstallLocation 2^>nul ^| find "InstallLocation"') do if exist "%%B\ISCC.exe" set "ISCC=%%B\ISCC.exe"
)
if not defined ISCC goto :error_inno
echo        %ISCC%
if not exist "instalador" mkdir "instalador"
"%ISCC%" /Qp "/DMiVersion=%VER%" "%CARPETA%instalador_accion.iss"
if errorlevel 1 goto :error_iscc
if not exist "instalador\Instalar_Accion_%VER%.exe" goto :error_iscc
echo        Listo: instalador\Instalar_Accion_%VER%.exe
if /i not "%IA%"=="si" goto :fin

REM --- 7. El instalador con la IA del Asesor adentro ---
echo.
echo  [7/7] Preparando la IA del Asesor (Ollama y el modelo %IA_MODELO%)...
if not exist "%VPY%" goto :error_sin_entorno
"%VPY%" "preparar_ia.py" --modelo "%IA_MODELO%" --nvidia "%IA_NVIDIA%" --zip "%OLLAMA_ZIP%"
if errorlevel 1 goto :error_ia
echo        Armando el instalador con IA (puede tardar varios minutos)...
set "OPC_IA=/DConIA=1"
if /i "%IA_NVIDIA%"=="si" set "OPC_IA=/DConIA=1 /DIANvidia=1"
"%ISCC%" /Qp "/DMiVersion=%VER%" %OPC_IA% "%CARPETA%instalador_accion.iss"
if errorlevel 1 goto :error_iscc
if not exist "instalador\Instalar_Accion_%VER%_con_IA.exe" goto :error_iscc
echo        Listo: instalador\Instalar_Accion_%VER%_con_IA.exe

:fin
echo.
echo  ====================================================================
echo   LISTO: instalador\Instalar_Accion_%VER%.exe
if /i "%IA%"=="si" echo          instalador\Instalar_Accion_%VER%_con_IA.exe  (con la IA del Asesor adentro)
echo  ====================================================================
echo   El de siempre es el que usan las actualizaciones automaticas.
echo   El "con_IA" es para instalar por primera vez: el Asesor funciona apenas
echo   se instala, sin internet y sin instalar nada mas.
echo   Para publicar la actualizacion: python publicar_actualizacion.py
echo.
start "" explorer /select,"%CARPETA%instalador\Instalar_Accion_%VER%.exe"
pause
exit /b 0

REM ====================================================================
REM El diccionario del corrector: el primero que sea el RLA-ES (con tildes)
REM entre la linea DICCIONARIO= (arriba), la carpeta de accion.py y las
REM carpetas diccionario y sistema. El antiguo (sin tildes, de origen
REM desconocido) no se empaqueta: si solo esta ese, sale con error 2.
:buscar_diccionario
set "DICC="
set "DICC_ANTIGUO="
for %%C in ("%DICCIONARIO%" "%CARPETA%es_palabras.txt.gz" "%CARPETA%diccionario\es_palabras.txt.gz" "%CARPETA%sistema\es_palabras.txt.gz") do (
  if not defined DICC if exist "%%~C" call :probar_diccionario "%%~C"
)
if defined DICC goto :dicc_encontrado
if defined DICC_ANTIGUO exit /b 2
exit /b 1
:dicc_encontrado
for %%P in ("%DICC%") do set "DICC_CARPETA=%%~dpP"
set "DICC_TIPO=(el diccionario RLA-ES, con tildes)"
exit /b 0

:probar_diccionario
if not exist "%VPY%" (
  set "DICC=%~1"
  exit /b 0
)
"%VPY%" -c "import gzip, sys; sys.exit(0 if gzip.open(sys.argv[1], 'rt', encoding='utf-8').readline().startswith('#') else 1)" "%~1" >nul 2>&1
if errorlevel 1 (
  set "DICC_ANTIGUO=%~1"
  exit /b 0
)
set "DICC=%~1"
exit /b 0

REM El diccionario y su licencia van en la carpeta "sistema" del programa
:poner_diccionario
call :buscar_diccionario
if errorlevel 2 exit /b 2
if errorlevel 1 exit /b 1
if not exist "compilacion\dist\Accion\sistema" mkdir "compilacion\dist\Accion\sistema"
copy /y "%DICC%" "compilacion\dist\Accion\sistema\es_palabras.txt.gz" >nul
if errorlevel 1 exit /b 1
REM (su licencia y su forma original: junto al diccionario o en la carpeta diccionario)
for %%D in (LICENCIA_diccionario.txt es_CL.aff es_CL.dic) do (
  if exist "%DICC_CARPETA%%%D" (
    copy /y "%DICC_CARPETA%%%D" "compilacion\dist\Accion\sistema\%%D" >nul
  ) else (
    if exist "diccionario\%%D" copy /y "diccionario\%%D" "compilacion\dist\Accion\sistema\%%D" >nul
  )
)
if not exist "compilacion\dist\Accion\sistema\LICENCIA_diccionario.txt" echo        [aviso] falta LICENCIA_diccionario.txt (los creditos y la licencia del diccionario)
exit /b 0

:probar_python
%* -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 set "PYBASE=%*"
exit /b 0

:error_venv
echo  No se pudo crear el entorno de Python (.venv_compilar).
goto :error

:error_pip
echo.
echo  No se pudieron instalar PySide6 o PyInstaller.
echo  Revisa la conexion a internet y vuelve a intentar.
goto :error

:error_codigo
echo.
echo  accion.py tiene un error (arriba dice en que linea). Corrigelo y vuelve a intentar.
goto :error

:error_version
echo  No pude leer la version de accion.py (la linea __version__ = "...").
goto :error

:error_pyinstaller
echo.
echo  PyInstaller no pudo armar el programa: revisa los mensajes de arriba.
echo  Si Accion esta abierto desde compilacion\dist, cierralo y vuelve a intentar.
echo  Para ver los errores del programa: compilar_instalador.bat consola
goto :error

:error_diccionario
echo.
echo  No encontre el diccionario del corrector (es_palabras.txt.gz) en:
echo      %DICCIONARIO%
echo  Ponlo ahi (o junto a accion.py), o cambia la linea DICCIONARIO= de este archivo.
goto :error

:error_diccionario_antiguo
echo.
echo  El unico diccionario que encontre es el ANTIGUO (sin tildes y de origen desconocido):
echo      %DICC_ANTIGUO%
echo  Ese no se puede repartir. Reemplazalo por el es_palabras.txt.gz nuevo (RLA-ES)
echo  y pon junto a el LICENCIA_diccionario.txt, es_CL.aff y es_CL.dic.
goto :error

:error_ia
echo.
echo  No se pudo preparar la IA del Asesor (arriba dice por que).
echo  El instalador normal SI quedo listo: instalador\Instalar_Accion_%VER%.exe
echo  Para no armar el de IA, cambia la linea  set "IA=si"  por  set "IA=no".
goto :error

:error_sin_entorno
echo  Falta el entorno .venv_compilar: corre compilar_instalador.bat sin opciones una vez.
goto :error

:error_sin_programa
echo  Todavia no hay programa compilado en compilacion\dist\Accion.
echo  Corre compilar_instalador.bat sin opciones (compila y arma el instalador).
goto :error

:error_inno
echo.
echo  No encontre Inno Setup (version 6 o 7). Bajalo desde https://jrsoftware.org/isdl.php
echo  y vuelve a correr este archivo con la opcion instalador (no recompila):
echo      compilar_instalador.bat instalador
echo  El programa ya quedo armado en compilacion\dist\Accion.
goto :error

:error_iscc
echo.
echo  Inno Setup no pudo armar el instalador: revisa los mensajes de arriba.
goto :error

:error
echo.
echo  No se termino. Revisa el mensaje de arriba.
echo.
pause
exit /b 1
