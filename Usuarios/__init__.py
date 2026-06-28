import secrets
from flask import Blueprint, render_template, redirect, url_for, flash
from extensions import admin as flask_admin, db, admin_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from Usuarios.admin import UserAdminView, RoleAdminView
from Usuarios.models import User, Role
from flask_security import hash_password
from Usuarios.forms import UserForm
from crm.models import Customers 
from Pedidos.models import Orders, OrderItems
from Produtos.models import Categories, Products

usuarios_bp = Blueprint('usuarios', __name__)

usuarios_bp.menu_items = [
    {
        'key': None,
        'name': 'Configurações',
        'icon': 'cogs',
        'order': 90,  # Valor alto joga o bloco para o final do menu
        'children': [
            {
                'key': 'admin.index',
                'name': 'Painel Administrativo',
                'icon': 'shield-alt'
            },
            {
                'key': 'usuarios.listar',
                'name': 'Usuários',
                'icon': 'shield-alt'
            },
            {
                'key': 'usuarios.criar',
                'name': 'Criar usuario',
                'icon': 'shield-alt'
            }
        ]
    }
]

# ROTA 1: Listar Usuários (Read)
@usuarios_bp.route('/usuarios')
@admin_required()
def listar():
    usuarios = User.query.all()
    return render_template('site/usuarios_lista.html', usuarios=usuarios)

# ROTA: Criar Usuário (Create)
@usuarios_bp.route('/usuarios/criar', methods=['GET', 'POST'])
@admin_required()
def criar():
    form = UserForm()
    
    # ALIMENTAÇÃO DINÂMICA NATIVA: 
    # Busca todas as Roles do banco e monta uma lista de tuplas [(id, nome), ...]
    form.roles.choices = [(role.id, role.name) for role in Role.query.all()]
    
    if form.validate_on_submit():
        # Busca no banco os objetos reais das Roles que o administrador selecionou
        roles_selecionadas = Role.query.filter(Role.id.in_(form.roles.data)).all()
        
        novo_usuario = User(
            email=form.email.data,
            password=hash_password(form.password.data), # Criptografia ativa
            is_staff=form.is_staff.data,
            is_superuser=form.is_superuser.data,
            active=form.active.data,
            roles=roles_selecionadas, # Vincula os objetos Many-to-Many
            fs_uniquifier=secrets.token_hex(16)
        )
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('usuarios.listar_usuarios'))
        
    return render_template('site/usuarios_form.html', form=form, titulo="Criar Usuário")


# SOLUÇÃO CRÍTICA DO ERRO 'cls': Criamos uma classe intermediária que ignora o argumento intruso
class SafeModelView(ModelView):
  """
  Classe de visualização customizada que intercepta e limpa o argumento 'cls'
  injetado erroneamente pelas versões recentes do Flask em requisições de view.
  """
  def index_view(self, *args, **kwargs):
    # Remove silenciosamente o argumento 'cls' se ele for enviado pelo decorador do Flask
    kwargs.pop('cls', None)
    return super(SafeModelView, self).index_view(*args, **kwargs)

  def details_view(self, *args, **kwargs):
    kwargs.pop('cls', None)
    return super(SafeModelView, self).details_view(*args, **kwargs)

  def edit_view(self, *args, **kwargs):
    kwargs.pop('cls', None)
    return super(SafeModelView, self).edit_view(*args, **kwargs)

  def create_view(self, *args, **kwargs):
    kwargs.pop('cls', None)
    return super(SafeModelView, self).create_view(*args, **kwargs)


def setup_admin(app):
  """
  Inicializa o painel administrativo Flask-Admin utilizando a nossa visualização
  segura contra erros de argumentos inválidos do ciclo de rotas.
  """
  admin = Admin(app, name='Painel de Controle', template_mode='bootstrap4')

  # CORREÇÃO DEFINITIVA: Trocamos o 'ModelView' genérico pelo nosso 'SafeModelView' customizado
  admin.add_view(SafeModelView(Categories, db.session, name="Categorias", category="Estoque"))
  admin.add_view(SafeModelView(Products, db.session, name="Produtos", category="Estoque"))
  admin.add_view(SafeModelView(Customers, db.session, name="Clientes", category="Vendas"))
  admin.add_view(SafeModelView(Orders, db.session, name="Pedidos", category="Vendas"))
  admin.add_view(SafeModelView(OrderItems, db.session, name="Itens dos Pedidos", category="Vendas"))


# Adiciona o gerenciamento de Usuários e Grupos ao menu do Admin
flask_admin.add_view(UserAdminView(User, db.session, name="Usuários", category="Segurança"))
flask_admin.add_view(RoleAdminView(Role, db.session, name="Grupos/Roles", category="Segurança"))
