#!/bin/bash
set -e

user_actuel=$(whoami)

if [ $user_actuel == 'root' ] ; then
        echo "N'exécutez pas le script en tant que root"
        exit 1
fi

sudo apt update

echo "Installation des paquets Debian nécessaires..."
sudo apt install -y mariadb-server python3 python3-pip python3.11-venv \
    libmariadb-dev build-essential pkg-config

echo "Dépendances système installées"

# Créer l'environnement virtuel Python


echo "Création de l'environnement virtuel Python..."
python3 -m venv venv
source venv/bin/activate

echo "Mise à jour de pip..."
pip install --upgrade pip

echo "Installation des dépendances Python..."
pip install gunicorn flask flask-sqlalchemy SQLAlchemy flask-mysqldb bcrypt fabric mariadb PyYAML

echo "Toutes les dépendances Python sont installées !"

echo

echo "Entrez le nom de l'utilisateur MySQL/MariaDB avec droits de création de BDD "
read -p "Si MariaDB vient d'être installé, le user est root et faites juste entrer pour le mot de passe : "

echo

echo "Création de la BDD et des tables..." 
echo

sudo mysql -u "$SQL_USER" -p <<MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS sae302;
CREATE USER IF NOT EXISTS 'qamu'@'localhost' IDENTIFIED BY 'qamu';
GRANT ALL PRIVILEGES ON sae302.* TO 'qamu'@'localhost' IDENTIFIED BY 'qamu';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

sudo mysql -u qamu -pqamu sae302 < app_bdd.sql

echo "✅ Base de données et utilisateur créés avec succès !"
echo
echo "L'utilisateur qamu avec le mdp qamu est utilisé par défaut pour se connecter à la BDD sae302"
echo "Vous pouvez modifier cet utilisateur si vous le souhaiter, il faudra lire la doc"
echo "Activez l'environnement virtuel avec : source venv/bin/activate"
