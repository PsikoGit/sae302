# README – Installation de l’application de supervision Flask

## Prérequis

Avant de commencer, assurez-vous d’avoir :

- Une infrastructure avec des machines sous Debian (ou dérivé) sous Linux.
- Accès SSH aux machines distantes que vous souhaitez superviser, avec authentification par clé asymétrique sans passphrase.
- Un utilisateur disposant des droits sudo sur les machines distantes pour configurer le groupe et les permissions.
- `mariadb-server` installé sur la machine centrale pour la base de données.

---

## Étape 1 – Préparer la machine centrale

1. Ouvrir un terminal sur la machine centrale.
2. Cloner le dépôt GitHub de l’application :

```bash
git clone https://github.com/PsikoGit/sae302.git
cd sae302
```

Lancer le script `install_dependencies.sh` pour installer toutes les dépendances nécessaires au bon fonctionnement de l'application

Modifier le fichier `app/config.yaml`, renseignez l'utilisateur avec lequel vous vous connectez en ssh sur les serveurs à superviser et renseignez le nom du fichier de votre clé privée. Il faut que votre clé privée se trouve obligatoirement dans le répertoire `~/.ssh/`

---

## Étape 2 – Configurer la base de données

Sur le serveur MariaDB, ajouter un utilisateur qamu@localhost avec le mot de passe qamu et lui donner tous les droits sur la base de données sae302 (vous avez le choix de changer d'utilisateur et de mot de passe, il faudra changer la ligne du fichier `config.py` : `SQLALCHEMY_DATABASE_URI = 'mariadb+mariadbconnector://qamu:qamu@localhost/sae302'`

Créer la base de données sae302 sur votre serveur MariaDB et faites un dump du fichier `app_bdd.sql` avec la commande : `sudo mysql -u votre_utilisateur -p sae302 < app_bdd.sql`

---

## Étape 3 – Configurer les machines à superviser

Créez un groupe dédié, par exemple superviseur : `sudo groupadd superviseur`

Ajoutez l’utilisateur SSH à ce groupe : `sudo usermod -aG superviseur mon_utilisateur`

Donnez à cet utilisateur des droits sudo sans mot de passe, mais seulement pour la commande spécifique utilisée par l’application `/usr/bin/tac /var/log/syslog` en modifiant `/etc/sudoers` : `sudo visudo`

Ajoutez la ligne suivante (en adaptant le nom de l’utilisateur) : `mon_utilisateur ALL=(ALL) NOPASSWD: /usr/bin/tac /var/log/syslog`

Assurez-vous que la machine distante est accessible depuis la machine centrale via SSH sur la couche 3 (ping et SSH fonctionnels).
