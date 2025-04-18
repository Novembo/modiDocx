@echo off
echo 🔧 Compilation modiDocx pour Windows...
pyinstaller modiDocx.spec --noconfirm
echo ✅ Compilation terminée. Fichier disponible dans \dist\modiDocx
pause
