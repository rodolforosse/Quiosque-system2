import secrets
from flask import Flask
from app.extensions import flask_admin, db, security
from flask_admin.menu import MenuLink
from flask_wtf.csrf import CSRFProtect
from flask_security import SQLAlchemyUserDatastore, hash_password
from admin.usuarios import SecureAdminIndexView 
from Blueprint import *
import app.models as models

# Objeto de proteção global
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '8a0687f5d5c648d98790961744e3f9ad'
    app.config['SECURITY_PASSWORD_SALT'] = 'c5d55a951180f3ff9a8fff4c062e56f110974305c6b614b4a837774992a1fe40'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECURITY_REGISTERABLE'] = False
    app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
    
    app.config['SECURITY_MSG_INVALID_PASSWORD'] = ('Senha inválida.', 'error')
    app.config['SECURITY_MSG_USER_DOES_NOT_EXIST'] = ('Este usuário não está cadastrado.', 'error')
    app.config['SECURITY_MSG_PASSWORD_NOT_SET'] = ('Senha não definida.', 'error')
    app.config['SECURITY_MSG_DISABLED_ACCOUNT'] = ('Esta conta foi desativada.', 'error')
    app.config['SECURITY_MSG_INVALID_EMAIL_ADDRESS'] = ('Endereço de e-mail inválido.', 'error')

    db.init_app(app)
    
    # Inicializa a proteção CSRF no aplicativo
    csrf.init_app(app)
    
    flask_admin.init_app(app, index_view=SecureAdminIndexView())

    flask_admin.add_link(MenuLink(name='Sair', endpoint='security.logout', category=''))
    
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security.init_app(app, user_datastore)
   
    # Registra todos os blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(caixa_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(produtos_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(crm_bp)

    with app.app_context():
        db.create_all()
        
        # Cria o Superusuário do sistema
        if not user_datastore.find_user(email='admin@teste.com'):
            user_datastore.create_user(
                email='admin@teste.com',
                password=hash_password('admin123'),
                is_superuser=True,
                is_staff=True,  
                fs_uniquifier=secrets.token_hex(16)
            )
        db.session.commit()

    @app.context_processor
    def inject_menu():
        lista_final_menus = []
        
        # Coleta os menus de todos os Blueprints registrados
        for _, blueprint in app.blueprints.items():
            if hasattr(blueprint, 'menu_items'):
                lista_final_menus.extend(blueprint.menu_items)
                
        # O parametro default garante que o app não quebre 
        # caso você esqueça de colocar 'order' em algum menu futuro
        lista_ordenada = sorted(
            lista_final_menus, 
            key=lambda item: item.get('order', 99)
        )
                
        return dict(menu_items=lista_ordenada)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
