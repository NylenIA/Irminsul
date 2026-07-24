@echo off
chcp 65001 >nul
title Irminsul
setlocal

rem === Lanceur Irminsul (mode navigateur, fiable) ===================
rem Ouvre l'application Irminsul dans ton navigateur. Ne PAS fermer
rem cette fenetre noire tant que tu utilises l'app (elle fait tourner
rem le serveur local). Ferme-la pour quitter.
rem =================================================================

set "REPO=%~dp0"
set "SERVERDIR=%REPO%app\src-tauri\web\standalone\apps\web"
set "SIDECAR=%REPO%app\src-tauri\binaries\irminsul-sidecar-x86_64-pc-windows-msvc.exe"

rem Donnees utilisateur (compte importe, equipes) = dossier de l'app installee.
set "APP=%APPDATA%\com.nylenia.irminsul"
set "IRMINSUL_DATA_DIR=%APP%\data"
rem Prisma veut des slashes avant.
set "DBP=%APP%\irminsul.db"
set "DATABASE_URL=file:%DBP:\=/%"

set "HOSTNAME=127.0.0.1"
set "PORT=3300"
set "NODE_ENV=production"
set "IRMINSUL_SIDECAR_EXE=%SIDECAR%"

if not exist "%SERVERDIR%\server.js" (
  echo [Irminsul] Build introuvable. Lance d'abord :  npm run desktop:prepare
  echo Puis relance ce fichier.
  pause
  exit /b 1
)

echo [Irminsul] Demarrage du serveur local...
echo [Irminsul] L'app va s'ouvrir dans ton navigateur sur http://127.0.0.1:%PORT%
echo [Irminsul] Garde cette fenetre ouverte pendant l'utilisation.

rem Ouvre le navigateur apres un court delai (le temps que le serveur soit pret).
start "" cmd /c "timeout /t 5 >nul & start "" http://127.0.0.1:%PORT%/"

cd /d "%SERVERDIR%"
node server.js

endlocal
