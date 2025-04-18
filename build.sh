#!/bin/bash
echo "🔧 Compilation modiDocx pour Linux/Mac..."
pyinstaller modiDocx.spec --noconfirm
echo "✅ Compilation terminée. Fichier disponible dans /dist/modiDocx"
