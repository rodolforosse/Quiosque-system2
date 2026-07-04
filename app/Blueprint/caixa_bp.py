# Caixa
from flask import Blueprint, render_template, jsonify
from app.extensions import admin_required
from app.models import Caixadb, MovimentacaoCaixa

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

# 1. ROTA: Painel de Caixa
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
    caixa_atual = Caixadb.query.filter_by(status='aberto').order_by(Caixadb.data_abertura.desc()).first()
    
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


# 2. ROTA: API JSON com as movimentações do caixa atual
@caixa_bp.route('/caixa/movimentacoes.json')
@admin_required()
def movimentacoes_json():
    """
    Retorna em JSON as movimentações do caixa aberto mais recente.
    Cada item inclui: id, order_id (sequencial), date (ISO), description, entrada, saida, metodo_pagamento
    """
    caixa_atual = Caixadb.query.filter_by(status='aberto').order_by(Caixadb.data_abertura.desc()).first()
    if not caixa_atual:
        return jsonify({'success': False, 'error': 'Nenhum caixa aberto localizado.'}), 404

    movs = MovimentacaoCaixa.query.filter_by(caixa_id=caixa_atual.id).order_by(MovimentacaoCaixa.data_movimento.asc()).all()
    resultado = []
    for m in movs:
        # Inclui vendas e devoluções e também movimentações vinculadas a pedidos
        if m.tipo not in ('venda', 'devolucao') and not m.order_id:
            continue

        entrada = float(m.valor) if m.tipo == 'venda' else 0.0
        saida = float(m.valor) if m.tipo == 'devolucao' else 0.0

        descricao = m.descricao.strip() if m.descricao else ''
        if not descricao and m.order:
            descricao = f"Pedido #{m.order.order_id} Balcão"

        resultado.append({
            'id': m.id,
            'order_id': m.order.order_id if m.order else None,
            'date': m.data_movimento.isoformat(),
            'description': descricao or m.tipo,
            'entrada': entrada,
            'saida': saida,
            'metodo_pagamento': m.metodo_pagamento
        })

    return jsonify({'success': True, 'movimentacoes': resultado}), 200
