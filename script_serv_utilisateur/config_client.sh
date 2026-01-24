#!/bin/bash

user_actuel=$(whoami)

if [ $user_actuel == 'root' ] ; then
        echo "N'exécutez pas le script en tant que root"
        exit 1
fi

#Met le format des journaux syslog dans le bon format pour l'application
sudo apt install -y rsyslog
sudo systemctl enable --now rsyslog

if [ ! -s /etc/rsyslog.d/00-bsd-format.conf ] ; then
	echo '$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat' | sudo tee -a /etc/rsyslog.d/00-bsd-format.conf
fi 

sudo systemctl restart rsyslog

echo "Création du groupe 'superviseur'"

sudo groupadd superviseur 

read -p "Entrez le nom d'utilisateur avec lequel vous allez vous connecter en SSH pour la visualisation des logs : " USER_SSH

if ! grep "^${USER_SSH}:" /etc/passwd > /dev/null ; then
	echo "L'utilisateur n'existe pas, créez-le"
	exit 1
fi

echo "Attribution de l'utilisateur au groupe 'superviseur'"

if sudo usermod -aG superviseur ${USER_SSH} ; then
	echo "Utilisateur attribué au groupe, configuration du fichier /etc/sudoers"
else
	echo "Erreur d'attribution de l'utilisateur au groupe 'superviseur'"
	exit 1
fi

if [ -s /etc/sudoers.d/command_tac ] ; then
	echo "Le fichier /etc/sudoers.d/command_tac existe déjà"
	exit
fi

sudo touch /etc/sudoers.d/command_tac

echo "%superviseur ALL=(root) NOPASSWD: /usr/bin/tac /var/log/syslog" | sudo tee -a /etc/sudoers.d/command_tac

sudo chown root:root /etc/sudoers.d/command_tac
sudo chmod 440 /etc/sudoers.d/command_tac

echo "Le fichier /etc/sudoers a été configuré, votre configuration sudoers est fonctionnel pour le fonctionnement de l'application"
