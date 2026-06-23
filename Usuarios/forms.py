# usuarios/formularios.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length

class UserForm(FlaskForm):
    name = StringField('Nome', validators=[
        DataRequired(message="O nome do usuário é obrigatório"), 
        Email(message="Digite o nome do usuário."), 
        Length(max=128)
    ])
    surname = StringField('Sobrenome', validators=[
        DataRequired(message="O nome do usuário é obrigatório"), 
        Email(message="Digite o nome do usuário."), 
        Length(max=255)
    ])
    email = StringField('E-mail', validators=[
        DataRequired(message="O e-mail é obrigatório."), 
        Email(message="Digite un e-mail válido."), 
        Length(max=255)
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message="A senha é obrigatória."),
        Length(min=6, max=255, message="A senha deve ter no mínimo 6 caracteres.")
    ])
    is_staff = BooleanField('Acesso Staff (Permite entrar no painel)')
    is_superuser = BooleanField('Superusuário (Poder absoluto)')
    active = BooleanField('Conta Ativa', default=True)
    
    # CAMPO NATIVO: Exibe uma caixa de múltipla seleção para os grupos (Roles)
    roles = SelectMultipleField('Grupos / Roles', coerce=int)
