from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import UsernameExistsError, UserNotFoundError, DatabaseError, IPExistsError, ServerNotFoundError
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Privilege(db.Model):
    __tablename__ = "privileges"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(100),nullable=False)

class Role(db.Model):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(50),nullable=False)
    privileges: Mapped[int] = mapped_column(Integer, nullable=False)

class Serveur(db.Model):
    __tablename__ = "serveurs"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    nom: Mapped[str] = mapped_column(String(100),nullable=False,unique=True)
    ip: Mapped[str] = mapped_column(String(15),nullable=False,unique=True)

    @staticmethod
    def ajoute_serveur(nom,ip):
        """ Ajoute un serveur dans la BDD """
        try:
            autre_nom = Serveur.query.filter_by(nom=nom).first()
            if autre_nom:
                raise UsernameExistsError("Un serveur porte déjà ce nom")

            autre_ip = Serveur.query.filter_by(ip=ip).first()
            if autre_ip:
                raise IPExistsError("Un serveur possède déjà cette IP")
            
            p = Serveur(nom=nom,ip=ip)
            db.session.add(p)
            db.session.commit()
        except (UsernameExistsError, IPExistsError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erreur lors de l'ajout en base : {e}")

    @staticmethod
    def maj_serveur(num_id,ip):
        """ Met à jour l'adresse IP du serveur """
        try:
            p = Serveur.query.get(num_id)
            if not p:
                raise ServerNotFoundError("Le serveur n'existe pas")

            exist = Serveur.query.filter_by(ip=ip).first()
            if exist and exist.id != int(num_id):
                raise IPExistsError("Un serveur avec cette adresse IP existe déjà")

            p.ip = ip
            db.session.commit()
        except (ServerNotFoundError,IPExistsError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erreur lors de la modification du serveur en base : {e}")

    @staticmethod
    def supprime_serveur(num_id):
        """ Supprime un serveur de la BDD """
        try:
            p = Serveur.query.get(num_id)
            if not p:
                raise ServerNotFoundError("Le serveur n'existe pas")
            db.session.delete(p)
            db.session.commit()
        except ServerNotFoundError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erreur lors de la suppresion de l'utilisateur en base : {str(e)}")

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    username: Mapped[str] = mapped_column(String(50),nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255),nullable=False)
    role_id: Mapped[int] = mapped_column(Integer,ForeignKey("roles.id"),nullable=False)

    def set_password(self, password):
        if password:
            self.password = generate_password_hash(password)

    def check_password(self, password):
        if password:
            return check_password_hash(self.password, password)

    @staticmethod
    def get_privilege(user_id,privilege_id):
        """ Vérifie si un utilisateur a le privilège 'privilege_id' """
        try:
            user = User.query.get(user_id) #On récupère l'objet correspondant au user
            if not user:
                return False
            role = Role.query.get(user.role_id) #On récupère l'objet correspondant au role du user
            if not role:
                return False
            return bool(role.privileges & privilege_id) #Comparaison booléenne 'OU' bit à bit 
        except SQLAlchemyError as e:
            print(f"Erreur dans get_privilege : {e}")
            return False


    @staticmethod
    def ajoute_user(nom,mdp,role_id):
        """ Ajoute un utilisateur dans la BDD """
        try:

            if User.query.filter_by(username=nom).first():
                raise UsernameExistsError(f"Le nom d'utilisateur {nom} existe déjà")

            hashed_pass = generate_password_hash(mdp)
            p = User(username=nom,password=hashed_pass,role_id=int(role_id))
            db.session.add(p)
            db.session.commit()

        except UsernameExistsError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erreur lors de l'ajout en base : {str(e)}")

    @staticmethod
    def maj_admin(nom,mdp):
        """ Modifie les informations du compte avec l'ID 1 (admin par défaut) """
        try:
            p = User.query.get(1)
            if not p: #Ça ne devrait pas arriver
                raise UserNotFoundError(f"L'utilisateur avec l'ID 1 n'a pas été trouvé dans la base de données")

            exist = User.query.filter_by(username=nom).first()
            if exist and exist.id != 1:
                raise UsernameExistsError(f"Le nom d'utilisateur {nom} existe déjà")

            p.username = nom
            p.set_password(mdp)
            db.session.commit()
        except (UserNotFoundError, UsernameExistsError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erreur lors de la modification de l'utilisateur ID 1 en base : {str(e)}")

    @staticmethod
    def supprime_user(num_id):
        """ Supprime l'utilisateur de la BDD """
        try:
            p = User.query.get(num_id)
            if not p:
                raise UserNotFoundError(f"Utilisateur avec l'ID {num_id} introuvable")
            db.session.delete(p)
            db.session.commit()
        except UserNotFoundError:
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erreur lors de la suppresion de l'utilisateur en base : {str(e)}")

    @staticmethod
    def maj_user(num_id,nom,mdp,role_id):
        """ Met à jour les informations de l'utilisateur dans la BDD """
        try:
            p = User.query.get(num_id)
            if not p:
                raise UserNotFoundError(f"Utilisateur avec l'ID {num_id} introuvable")

            exist = User.query.filter_by(username=nom).first()
            if exist and exist.id != int(num_id):
                raise UsernameExistsError(f"Le nom d'utilisateur {nom} existe déjà")

            p.username = nom
            p.set_password(mdp)
            p.role_id = role_id
            db.session.commit()

        except (UserNotFoundError, UsernameExistsError):
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erreur lors de la modification de l'utilisateur en base : {str(e)}")
