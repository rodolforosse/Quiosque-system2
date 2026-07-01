from datetime import datetime
from flask import Blueprint, render_template
from flask_login import current_user
from app.extensions import admin_required

# Cria o blueprint de Caixa
profile_bp = Blueprint('profile', __name__)

# 1. ROTA: Painel de Caixa
@profile_bp.route('/profile')
@admin_required()
def create_view():
    """
    Exibe o profile de usuário com:
    - Botão de registro de ponto
    - Board de informativos
    - Link para ajustes de ponto e plantão
    """
    
    # Dados do profile do usuário
    profile_info = {
        'ultimo_registro': datetime.now(),
        # 'user_id': g.user_id (Ajuste que fizemos no começo)
    }
    
    return render_template('site/profile.html', profile_info=profile_info)

@profile_bp.route('/profile/espelho_ponto')
@admin_required()
def espelho_colaborador():
    return "teste 123"