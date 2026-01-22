# Installation de l’application de supervision Flask

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

Pour la configuration de la base de données, ça se fera automatiquement quand vous lancerez le script `install_dependencies.sh`. Par défaut, l'utilisateur qamu@localhost avec le mot de passe qamu est utilisé pour se connecter à la BDD pour l'application. 

Si vous désirez changer d'utilisateur pour la connexion à la BDD, il faudra lui donner tous les droits sur la BDD sae302 et changer la ligne `SQLALCHEMY_DATABASE_URI = 'mariadb+mariadbconnector://qamu:qamu@localhost/sae302'` dans le fichier `sae302/config.py`, remplacer `qamu:qamu` par `user:password` 

---

## Étape 3 – Configurer les machines à superviser

Pour configurer les machines à superviser, il faudra importer les scripts `script_serv_utilisateur/config_sudoers.sh`et `script_serv_utilisateur/ssh-limiter.sh` sur les machines.

Puis lancer le script `config_sudoers.sh`, ce script créera le groupe `superviseur` avec les droits sudo sans **mot de passe** et ajoutera votre utilisateur dans ce groupe pour le bon fonctionnement de l'application

Sur les clients, il faudra sécurisé dans le fichier `~/.ssh/authorized_keys` et ajouter l'instruction `command="chemin_vers_le_fichier/ssh-limiter.sh",no-port-forwarding,no-X11-forwarding,no-agent-forwarding` devant la clé publique du serveur de supervision

Assurez-vous que la machine distante est accessible depuis la machine centrale via SSH sur la couche 3 (ping et SSH fonctionnels).
