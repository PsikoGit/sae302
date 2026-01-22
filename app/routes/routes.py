#Import des exceptions
from app.exceptions import UsernameExistsError,InvalidUsernameError,InvalidPasswordError
from app.exceptions import InvalidRoleError,UserNotFoundError,DatabaseError
from app.exceptions import IPExistsError,ServerNotFoundError, PasswordError, ServerConnectionError
from paramiko.ssh_exception import NoValidConnectionsError, SSHException
from sqlalchemy.exc import SQLAlchemyError

#Import des fonctions/BDD
from app.models.models import Privilege, Role, User, Serveur
from app.annexes import verif_session_et_privilege, verif_user, verif_ip
from app.ssh import get_log
from flask import Blueprint, render_template, redirect, request, session

import ipaddress

user_bp = Blueprint('user',__name__,template_folder='../templates')

@user_bp.route('/')
@user_bp.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username.strip() and password.strip():
        
            try:
                user = User.query.filter_by(username=username).first() 
            except SQLAlchemyError as e:
                msg = f"Erreur de connexion à la BDD, regardez le fichier app/config.py, erreur : {e}"
                return render_template('login.html',msg=msg)
                
            if user and user.check_password(password):
                session['loggedin'] = True
                session['id'] = user.id
                session['username'] = user.username
                return render_template('index.html', msg="Connecté avec succés!",user=user)
        return render_template('login.html',msg="Nom d'utilisateur/Mot de passe incorrect!")
    #Si c'est une requête 'GET'
    if 'id' in session:
        user = User.query.get(session['id'])
        return render_template('index.html',user=user)
    else:
        return render_template('login.html',msg='')

@user_bp.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    return redirect('/login')

#=======================================================
# Tous les chemins liés à la consultation des journaux ||
#=======================================================

@user_bp.route('/journaux')
def journaux():
    result = verif_session_et_privilege(1)
    if result:
        return result

    user = User.query.get(session['id'])
    return render_template('user/journaux.html',user=user,liste=Serveur.query.all())

@user_bp.route('/journaux_log',methods=['POST'])
def journaux_log():
    result = verif_session_et_privilege(1)
    if result:
        return result

    user = User.query.get(session['id'])

    if request.method == 'POST':

        lines = ''
        msg = ''
        server = request.form.getlist("servers")
        
        if server:
        
            try:
                lines = get_log(server)
            except FileNotFoundError as e:
                msg = e
            except ServerConnectionError as e:
                msg = e

    return render_template('user/journaux_log.html',liste_server=server,user=user,lines=lines,msg=msg)

#==================================================
# Tous les chemins liés à la gestion des machines ||
#==================================================

@user_bp.route('/machines',methods=['GET','POST'])
def machines():
    result = verif_session_et_privilege(2)
    if result:
        return result    

    user = User.query.get(session['id'])  
    msg = ''

    if request.method == 'POST':

        nom = request.form.get('nom')
        ip = request.form.get('ip')

        try:
            verif_user(nom=nom)
            verif_ip(ip)
            Serveur.ajoute_serveur(nom,ip)
        except InvalidUsernameError as e:
            msg = f"{e.message}"
        except ipaddress.AddressValueError as e:
            msg = f"Adresse IP Invalide : {e}"
        except UsernameExistsError as e:
            msg = f"{e.message}"
        except IPExistsError as e:
            msg = f"{e.message}"
        except DatabaseError as e:
            msg = f"{e.message}"

    return render_template('gestionnaire/machines.html',user=user,liste=Serveur.query.all(),msg=msg)

@user_bp.route('/modif_machine/<int:ref>',methods=['GET','POST'])
def modif_machine(ref):
    result = verif_session_et_privilege(2)
    if result:
        return result

    user = User.query.get(session['id'])
    p = Serveur.query.get(ref)

    if request.method == "POST":
        ip = request.form.get("ip")

        try:
            verif_ip(ip)
            Serveur.maj_serveur(ref,ip)
            msg = f"L'IP de la machine '{p.nom}' a été modifié avec succès"
        except ipaddress.AddressValueError as e:
            msg = f"Le format de l'IP est invalide : {e}"
        except ServerNotFoundError as e:
            msg = f"{e.message}"
        except IPExistsError as e:
            msg = f"{e.message}"
        except DatabaseError as e:
            msg = f"{e.message}"

        return render_template('gestionnaire/machines.html',user=user,liste=Serveur.query.all(),msg=msg)

    #Si c'est une requête GET
    msg = ''
    if not p:
        msg = 'Vous essayez de modifier un serveur inexistant'
    return render_template('gestionnaire/modif_machines.html',user=user,p=p,msg=msg)
    
@user_bp.route('/delete_machine/<int:ref>',methods=['POST'])
def delete_machine(ref):
    result = verif_session_et_privilege(2)
    if result:
        return result

    try:
        serv = Serveur.query.get(ref)
        Serveur.supprime_serveur(ref)
        msg = f"Le serveur '{serv.nom}' a été supprimé avec succés"
    except DatabaseError as e:
        msg = f"{e.message}"
    except ServerNotFoundError as e:
        msg = f"{e.message}"

    return render_template('gestionnaire/machines.html',user=User.query.get(session['id']),liste=Serveur.query.all(),msg=msg)

#=======================================================
# Tous les chemins liés à la gestion des utilisateurs  ||
#=======================================================

@user_bp.route('/utilisateurs',methods=['GET','POST'])
def utilisateurs():
    result = verif_session_et_privilege(4)       
    if result:
        return result

    user = User.query.get(session['id'])
    msg = ''

    if request.method == 'POST':

        nom = request.form.get('username')
        mdp = request.form.get('password')
        mdp2 = request.form.get('password2')
        role = request.form.get('role_id')

        try:
            if mdp != mdp2:
                raise PasswordError("Les mots de passes sont différents, réessayez")
                
            verif_user(nom,mdp,role) #Si quelque chose se passe mal une erreur sera levée
            User.ajoute_user(nom,mdp,role) #Idem
            msg = "L'utilisateur a été ajouté avec succès"
            return render_template('admin/utilisateurs.html',user=user,liste=User.query.all(),msg=msg)

        except PasswordError as e:
            msg = f"{e.message}"
        except UsernameExistsError as e:
            msg = f"{e.message}"
        except InvalidUsernameError as e:
            msg = f"{e.message}: entre 3 et 20 caractères contenant des lettres minuscules et majuscules, des chiffres, tiret du bas et tiret du haut"
        except InvalidPasswordError as e:
            msg = f"{e.message}"
        except InvalidRoleError as e:
            msg = f"{e.message}"
        except DatabaseError as e:
            msg = f"{e.message}"

        return render_template('admin/add_utilisateurs.html',user=user,msg=msg)

    #Si c'est une requête GET
    return render_template('admin/utilisateurs.html',user=user,liste=User.query.all(),msg=msg)

@user_bp.route('/add_utilisateurs',methods=['GET'])
def add_utilisateurs():
    result = verif_session_et_privilege(4)
    if result:
        return result
        
    user = User.query.get(session['id'])
    return render_template('admin/add_utilisateurs.html',user=user,msg='')

@user_bp.route('/modif_user/<int:ref>',methods=['GET','POST'])
def modif_user(ref):
    result = verif_session_et_privilege(4)
    if result:
        return result

    user = User.query.get(session['id'])  
    p = User.query.get(ref)

    if request.method == "POST":
        nom = request.form.get("username")
        mdp = request.form.get("password")
        mdp2 = request.form.get("password2")
        try:
            if mdp != mdp2:
                raise PasswordError("Les mots de passes sont différents, réessayez")

            if ref != 1:
                role = request.form.get("role_id")
                verif_user(nom,mdp,role) #La fonction génèrera une exception si quelque chose se passe mal
                User.maj_user(ref,nom,mdp,role) #Idem
                msg = f"L'utilisateur dont l'ID est <{ref}> a été modifié avec succès"
            else:
                verif_user(nom=nom,mdp=mdp)
                User.maj_admin(nom,mdp)
                msg = f"L'utilisateur avec l'ID <1> a été modifié avec succès"
            return render_template('admin/utilisateurs.html',user=user,liste=User.query.all(),msg=msg)

        except PasswordError as e:
            msg = f"{e.message}"
        except UsernameExistsError as e:
            msg = f"{e.message}"
        except InvalidUsernameError as e:
            msg = f"{e.message}"
        except InvalidPasswordError as e:
            msg = f"{e.message}"
        except InvalidRoleError as e:
            msg = f"{e.message}"
        except DatabaseError as e:
            msg = f"{e.message}"
        except UserNotFoundError as e:
            msg = f"{e.message}"

        return render_template('admin/modif_utilisateurs.html',user=user,msg=msg,p=p,inexist='')     

    #Si c'est une requête 'GET'
    inexist = ''
    if not p:
        inexist = 'Vous essayez de modifier un utilisateur inexistant'
    return render_template('admin/modif_utilisateurs.html',user=user,p=p,msg='',inexist=inexist)


@user_bp.route('/delete_user/<int:ref>',methods=['POST'])
def delete_user(ref):
    result = verif_session_et_privilege(4)
    if result:
        return result

    if ref == 1:
        msg = "Vous ne pouvez pas supprimer le compte avec l'ID 1"
    else:
        try:
            user = User.query.get(ref)
            User.supprime_user(ref)
            msg = f"Utilisateur {user.username} avec l'ID <{ref}> a été supprimé avec succés"
        except DatabaseError as e:
            msg = f"{e.message}" 
        except UserNotFoundError as e:
             msg = f"{e.message}"

    return render_template('admin/utilisateurs.html',user=User.query.get(session['id']),liste=User.query.all(),msg=msg)
