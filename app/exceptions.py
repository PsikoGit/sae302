class AppException(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ServerConnectionError(AppException):
    def __init__(self,server,original_exception):
        self.server = server
        self.original_exception = original_exception
        super().__init__(f"Erreur sur le serveur {server}: {original_exception}")

class PasswordError(AppException):
    """ Si les mots de passe ne correspondent pas"""
    pass

class ServerNotFoundError(AppException):
    """ Le serveur n'existe pas """
    pass

class IPExistsError(AppException):
    """ Un serveur possède déjà cette IP """
    pass

class UsernameExistsError(AppException):
    """Le nom d'utilisateur existe déjà"""
    pass

class InvalidUsernameError(AppException):
    """Le format du nom d'utilisateur est invalide"""
    pass

class InvalidPasswordError(AppException):
    """Le format du mot de passe est invalide"""
    pass

class InvalidRoleError(AppException):
    """Le rôle n'existe pas"""
    pass

class UserNotFoundError(AppException):
    """L'utilisateur n'existe pas"""
    pass

class DatabaseError(AppException):
    """Erreur lors de l'opération en base de données"""
    pass
