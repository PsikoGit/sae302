from flask import redirect, session, render_template
from app.models.models import Role, User
from app.exceptions import UsernameExistsError,InvalidUsernameError,InvalidPasswordError,InvalidRoleError,UserNotFoundError,DatabaseError

def verif_session():
    """ Vérifie si une session est en cours """
    if 'id' not in session:
        return redirect('/login')

def verif_session_et_privilege(n):
    """Vérifie session + privilège,
    privilège 1 = consultation des journaux
    privilège 2 = gestion des machines
    privilège 4 = gestion des utilisateurs """
    
    privilege_valide = [1,2,4]
    if n not in privilege_valide:
        raise ValueError(f"Privilège invalide : {n}, les privilèges valides sont : {privilege_valide}") 
    result = verif_session()
    if result:
        return result
    if not User.get_privilege(session['id'],n):
        return render_template('not_allowed.html')    

def verif_user(nom=None,mdp=None,role_id=None):
    """Vérifie les données d'un utilisateur avant ajout/modification"""

    try:
        import re
        pattern = r'^[a-zA-Z][a-zA-Z0-9_-]{2,19}$'
        if nom is not None:
            if not isinstance(nom,str) or not re.match(pattern,nom):
                raise InvalidUsernameError("Format du nom d'utilisateur invalide : entre 3 et 20 caractères commençant par une lettre")

        if mdp is not None:
            if not isinstance(mdp, str) or len(mdp.strip()) < 8: #Rajouter 8 caratere minimal
                raise InvalidPasswordError("Le mot de passe doit contenir au moins 8 caractères")

        if role_id is not None:
            role_existe = Role.query.get(role_id)
            if not role_existe or not role_id.strip() or not role_id.isdigit():
                raise InvalidRoleError("Le rôle n'existe pas")    

    except (InvalidUsernameError, InvalidPasswordError, InvalidRoleError):
        raise

def verif_ip(ip):
    import ipaddress
    try:
        ipaddress.IPv4Address(ip)
    except ipaddress.AddressValueError:
        raise
