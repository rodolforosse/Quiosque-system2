# Caixa/__init__.py
from flask import Blueprint, render_template
from extensions import admin as flask_admin, db, admin_required
from Caixa.admin import CaixaAdminView, MovimentacaoCaixaAdminView
from Caixa.models import Caixa, MovimentacaoCaixa

# Registra as views de admin
flask_admin.add_view(CaixaAdminView(Caixa, db.session, name="Caixas", category="Financeiro"))
flask_admin.add_view(MovimentacaoCaixaAdminView(MovimentacaoCaixa, db.session, name="Movimentações", category="Financeiro"))

# Cria o blueprint de Caixa
caixa_bp = Blueprint('caixa', __name__)

caixa_bp.menu_items = [
    {
        'key': 'caixa.create_view',
        'name': 'Caixa',
        'icon': 'calculator',
        'order': 15,  # Logo após Dashboard
        'children': []
    }
]

# 1. ROTA: Painel de Caixa (ex: http://127.0.0.1/caixa)
@caixa_bp.route('/caixa')
@admin_required()
def create_view():
    """
    Exibe o painel de ponto de venda com:
    - Caixa aberto atual
    - Resumo de movimentações
    - Opções de operações (venda, devolução, etc)
    """
    # Busca o caixa aberto
    caixa_atual = Caixa.query.filter_by(status='aberto').order_by(Caixa.data_abertura.desc()).first()
    
    # Se houver caixa aberto, calcula dados em tempo real
    dados_caixa = {}
    if caixa_atual:
        movimentacoes = MovimentacaoCaixa.query.filter_by(caixa_id=caixa_atual.id).all()
        dados_caixa = {
            'caixa_id': caixa_atual.id,
            'valor_inicial': float(caixa_atual.valor_inicial),
            'valor_vendas': float(caixa_atual.valor_vendas),
            'valor_devolucoes': float(caixa_atual.valor_devolucoes),
            'valor_atual': float(caixa_atual.valor_inicial) + caixa_atual.total_operacoes,
            'total_movimentacoes': len(movimentacoes)
        }
    
    return render_template('site/caixa.html', caixa=dados_caixa)
