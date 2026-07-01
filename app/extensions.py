# extensoes.py
from functools import wraps
from flask import abort
from flask_login import current_user
from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme
from flask_security import Security
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Instancia vazia e limpa para evitar qualquer importação circular
flask_admin = Admin(name='Painel', theme=Bootstrap4Theme(swatch='flatly'))
security = Security()

# Seu novo decorator centralizado
def admin_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            
            is_superuser = getattr(current_user, 'is_superuser', False)
            is_staff = getattr(current_user, 'is_staff', False)
            
            if not (is_superuser or is_staff):
                return abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
