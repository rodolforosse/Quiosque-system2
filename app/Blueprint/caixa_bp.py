# Caixa
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import current_user
from decimal import Decimal
from app.extensions import admin_required, db
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
@caixa_bp.route('/caixa', methods=['GET', 'POST'])
@admin_required()
def create_view():
    """
    Exibe o painel de ponto de venda com:
    - Caixa aberto atual
    - Resumo de movimentações
    - Opções de operações (venda, devolução, etc)
    Suporta POST para abrir o caixa via formulário (campo 'saldo_inicial').
    """
    # Se for um POST vindo do formulário de abertura de caixa, processa a requisição
    if request.method == 'POST':
        # Apenas um tratamento simples: cria um novo caixa se não existir caixa aberto
        saldo_raw = request.form.get('saldo_inicial', '').strip()
        try:
            # Normaliza formato como "R$ 45,60" ou "45,60"
            saldo_norm = saldo_raw.replace('R$', '').replace('r$', '').replace('.', '').replace(',', '.')
            valor_inicial = Decimal(saldo_norm) if saldo_norm else Decimal('0.00')
        except Exception:
            valor_inicial = Decimal('0.00')

        # Só cria se realmente não houver caixa aberto
        existing = Caixadb.query.filter_by(status='aberto').order_by(Caixadb.data_abertura.desc()).first()
        if existing:
            flash('Já existe um caixa aberto. Feche-o antes de abrir outro.', 'warning')
            return redirect(url_for('caixa.create_view'))

        # Garante que há um usuário autenticado (admin_required garante isso)
        try:
            novo_caixa = Caixadb(status='aberto', valor_inicial=valor_inicial, user_abertura_id=current_user.id)
            db.session.add(novo_caixa)
            db.session.commit()
            flash('Caixa aberto com sucesso.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao abrir o caixa: {str(e)}', 'danger')

        return redirect(url_for('caixa.create_view'))

    # GET: busca o caixa aberto
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
