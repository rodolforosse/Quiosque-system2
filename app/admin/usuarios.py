# usuarios/admin.py
from flask import redirect, url_for, request, abort
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from app.models import User, Role

# REGRAS DE ACESSO DA PÁGINA INICIAL /ADMIN
class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        # Estilo Django: Pode entrar se for Superusuário OU se fizer parte do Staff
        return current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff)

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated:
            abort(403) # Logado mas sem permissão de Staff
        return redirect(url_for('security.login', next=request.url))


# BASE PROTEGIDA PARA TODAS AS TABELAS DO BANCO
class SecureModelView(ModelView):
    def is_accessible(self):
        # Verifica se o usuário tem o direito básico de visualizar tabelas do painel
        return current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff)

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated:
            abort(403)
        return redirect(url_for('security.login', next=request.url))

    # REPLICANDO O COMPORTAMENTO DE PERMISSÕES DO DJANGO:
    def can_create(self):
        # Superusuário faz tudo. Staff precisa da permissão 'add_<nome_da_tabela>'
        perm = f"add_{self.model.__tablename__}"
        return current_user.is_superuser or current_user.has_permission(perm)

    def can_edit(self):
        perm = f"change_{self.model.__tablename__}"
        return current_user.is_superuser or current_user.has_permission(perm)

    def can_delete(self):
        perm = f"delete_{self.model.__tablename__}"
        return current_user.is_superuser or current_user.has_permission(perm)


class UserAdminView(SecureModelView):
    # Exibe em formato de colunas clicáveis
    column_list = ['id', 'email', 'is_staff', 'is_superuser', 'active']
    # Define os campos visíveis no formulário de criação
    form_columns = ['email', 'password', 'is_staff', 'is_superuser', 'active', 'roles']

    def __init__(self, session, **kwargs):
        super(UserAdminView, self).__init__(User, session, **kwargs)

class RoleAdminView(SecureModelView):
    column_list = ['id', 'name', 'description', 'permissions']

    def __init__(self, session, **kwargs):
        super(RoleAdminView, self).__init__(Role, session, **kwargs)
