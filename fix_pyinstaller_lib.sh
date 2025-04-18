#!/bin/bash

echo "📦 Installation des dépendances nécessaires..."
sudo apt update && sudo apt install -y \
    build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libssl-dev libreadline-dev libffi-dev wget

echo "⬇️ Téléchargement de Python 3.10.14..."
cd /tmp
wget https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tgz
tar -xf Python-3.10.14.tgz
cd Python-3.10.14

echo "⚙️ Configuration avec --enable-shared..."
./configure --enable-optimizations --enable-shared

echo "🛠️ Compilation (cela peut prendre quelques minutes)..."
make -j$(nproc)

echo "📥 Installation..."
sudo make altinstall

echo "✅ Python 3.10 installé avec les bibliothèques partagées."

echo ""
echo "ℹ️ Si PyInstaller ne trouve toujours pas la lib, ajoute ceci à ton ~/.bashrc ou ~/.zshrc :"
echo "export LD_LIBRARY_PATH=/usr/local/lib:\$LD_LIBRARY_PATH"
echo ""
echo "Puis recharge avec : source ~/.bashrc (ou ~/.zshrc)"
