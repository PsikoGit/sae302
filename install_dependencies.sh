#!/bin/bash
set -e

sudo apt update


echo "Installation des paquets Debian nécessaires..."
sudo apt install -y mariadb-server python3 python3-pip python3.11-venv \
    libmariadb-dev build-essential wget

echo "Dépendances système installées"

# Créer l'environnement virtuel Python


echo " Création de l'environnement virtuel Python..."
python3 -m venv venv
source venv/bin/activate

echo " Mise à jour de pip..."
pip install --upgrade pip

echo " Installation des dépendances Python..."
pip install gunicorn flask flask-sqlalchemy SQLAlchemy flask-mysqldb bcrypt fabric mariadb

echo " Toutes les dépendances Python sont installées !"
echo " Activez l'environnement virtuel avec : source venv/bin/activate"
