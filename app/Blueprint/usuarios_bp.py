import secrets
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_security import hash_password
from app.extensions import db, admin_required
from app.forms import UserForm
from app.models import (
  User, 
  Role
)

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
