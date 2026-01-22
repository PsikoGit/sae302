# Utilisation de l’application de supervision des journaux

## Présentation générale

Cette application permet de superviser et consulter les journaux système (`/var/log/syslog`) d’un parc de serveurs GNU/Linux à distance.

Les journaux sont récupérés via une connexion SSH sécurisée et affichés dans une interface web développée avec Flask.

---

## Lancer l'application

Pour lancer l'application il faudra exécuter le fichier `run.py` qui se trouve dans le répertoire parent, aller sur un navigateur sur le lien `localhost:5000` 

## Principe de fonctionnement

- Les serveurs à superviser sont enregistrés dans une base de données.
- L’application se connecte aux machines distantes via SSH pour lire les journaux.
- Les utilisateurs doivent être **authentifiés** pour accéder à l’application.
- Les droits d’accès dépendent du **rôle** attribué à chaque utilisateur.

---

## Utilisateurs, rôles et privilèges

Chaque utilisateur possède un **rôle**, qui détermine ses **privilèges**.

### Privilèges disponibles

| Identifiant | Nom                          |
|------------|------------------------------|
| 1          | Consultation des journaux    |
| 2          | Gestion des serveurs         |
| 4          | Administration des utilisateurs |

Chaque privilège est une puissance de 2, ce qui permet de les combiner.

---

### Rôles définis

| Identifiant | Nom              | Privilèges |
|------------|------------------|------------|
| 1          | utilisateur      | 1          |
| 2          | gestionnaire     | 3 (1 + 2)  |
| 3          | administrateur   | 7 (1 + 2 + 4) |

- **Utilisateur** : peut uniquement consulter les journaux.
- **Gestionnaire** : peut consulter les journaux et gérer les serveurs.
- **Administrateur** : peut tout faire, y compris gérer les utilisateurs et leurs droits.

⚠️ Seuls les utilisateurs ayant le rôle **administrateur** peuvent gérer les utilisateurs.

---

## Connexion à l’application

- L’accès à l’application nécessite une authentification.
- Toute tentative d’accès sans session active redirige automatiquement vers la page de connexion.
- Une fois connecté, l’utilisateur accède à l’interface principale avec un menu adapté à ses droits.

---

## Interface utilisateur

Un menu principal est affiché en permanence en haut de l’écran :

- **Journaux** : consultation des journaux
- **Serveurs** : gestion des machines supervisées
- **Utilisateurs** : gestion des utilisateurs et des rôles
- **Déconnexion** : fermeture de la session

Les options du menu sont :
- actives si l’utilisateur possède les droits nécessaires
- visibles mais grisées si l’utilisateur n’a pas les privilèges requis

---

## Consultation des journaux

### Accès

Accessible aux utilisateurs ayant le privilège **consultation des journaux**.

### Fonctionnement

1. Sélectionner un ou plusieurs serveurs dans la liste.
2. Choisir le type de journal (actuellement : `syslog`).
3. Valider la sélection.

Les journaux sont alors affichés, les événements les plus récents apparaissent en premier.

---

## Gestion des serveurs

### Accès

Réservé aux utilisateurs ayant le rôle **gestionnaire** ou **administrateur**.

### Informations stockées

Pour chaque machine supervisée :
- Nom du serveur
- Adresse IP

### Opérations disponibles

#### Ajout d’un serveur
- Renseigner le nom et l’adresse IP
- Cliquer sur **Ajouter**
- Le serveur est enregistré dans la base de données

#### Suppression d’un serveur
- Sélectionner un serveur dans la liste
- Cliquer sur **Supprimer**
- Le serveur est retiré de la base de données

#### Modification d’un serveur
- Sélectionner un serveur
- Cliquer sur **Modifier**
- Modifier uniquement l’adresse IP
- L’IP est validée avant l’enregistrement

En cas d’erreur (IP invalide, conflit, etc.), un message explicite est affiché.

---

## Gestion des utilisateurs

### Accès

Réservé exclusivement aux utilisateurs ayant le rôle **administrateur**.

### Informations utilisateur

Chaque utilisateur est défini par :
- un identifiant unique
- un nom d'utilisateur de 3 à 20 caractères qui commence par une lettre et peut :
peut contenir des lettres minuscules et majuscules, contenir des chiffres, des tirets (`-`) et underscore (`_`) 
- un mot de passe qui fera au moins 8 caractères
- un rôle

### Opérations disponibles

- Ajout d’un utilisateur
- Modification d’un utilisateur
- Suppression d’un utilisateur
- Attribution ou modification du rôle

Les changements sont immédiatement enregistrés en base de données.

---

## Conclusion

Cette application fournit une solution centralisée et sécurisée pour :
- consulter les journaux système d’un parc de serveurs
- gérer les machines supervisées
- administrer les utilisateurs et leurs droits

Elle est conçue pour être évolutive et adaptable à d’autres types de journaux à l’avenir.
