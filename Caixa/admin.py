# Caixa/admin.py
from flask import redirect, url_for, request
from Usuarios.admin import SecureModelView
from Caixa.models import Caixa, MovimentacaoCaixa


def formatar_moeda(view, context, model, name):
    """Formatador para exibir valores monetários em Real (R$)"""
    valor = getattr(model, name)
    if valor:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ 0,00"


class CaixaAdminView(SecureModelView):
    """
    Painel administrativo para gerenciamento de Caixas/Turnos
    Controla abertura, fechamento e auditoria de movimentações
    """
    # 1. Configurações de Permissões CRUD
    can_create = True
    can_edit = True
    can_delete = False  # Nunca deletar registros de caixa (auditoria)
    can_view_details = True
    
    # 2. Configurações de Exibição
    column_list = [
        'id', 'data_abertura', 'status', 'valor_inicial', 
        'valor_vendas', 'valor_devolucoes', 'valor_final'
    ]
    
    column_labels = {
        'id': 'ID',
        'data_abertura': 'Abertura',
        'data_fechamento': 'Fechamento',
        'status': 'Status',
        'valor_inicial': 'Valor Inicial',
        'valor_vendas': 'Valor Vendas',
        'valor_devolucoes': 'Devoluções',
        'valor_final': 'Valor Final',
        'user_abertura': 'Aberto Por',
        'user_fechamento': 'Fechado Por',
        'observacoes': 'Observações'
    }
    
    # 3. Formatação de colunas monetárias
    column_formatters = {
        'valor_inicial': formatar_moeda,
        'valor_vendas': formatar_moeda,
        'valor_devolucoes': formatar_moeda,
        'valor_final': formatar_moeda,
    }
    
    # 4. Busca e Filtros
    column_searchable_list = ['id', 'status']
    column_filters = ['status', 'data_abertura', 'data_fechamento']
    column_default_sort = ('data_abertura', True)  # Mais recentes primeiro
    
    # 5. Formulário de Edição (Apenas certos campos editáveis)
    form_columns = [
        'status', 'valor_vendas', 'valor_devolucoes', 
        'valor_final', 'data_fechamento', 'user_fechamento', 'observacoes'
    ]
    
    # 6. Choices para status
    form_choices = {
        'status': [
            ('aberto', 'Aberto'),
            ('fechado', 'Fechado')
        ]
    }


class MovimentacaoCaixaAdminView(SecureModelView):
    """
    Painel de auditoria completa de movimentações de caixa
    Vinculada aos pedidos para rastreamento total
    """
    # 1. Configurações de Permissões CRUD
    can_create = False  # Movimentações são criadas automaticamente pelo sistema
    can_edit = False
    can_delete = False  # Nunca deletar por auditoria
    can_view_details = True
    
    # 2. Configurações de Exibição
    column_list = [
        'id', 'caixa', 'tipo', 'valor', 'metodo_pagamento', 
        'data_movimento', 'user', 'order'
    ]
    
    column_labels = {
        'id': 'ID',
        'caixa': 'Caixa',
        'tipo': 'Tipo',
        'valor': 'Valor',
        'metodo_pagamento': 'Método Pagamento',
        'data_movimento': 'Data/Hora',
        'user': 'Usuário',
        'order': 'Pedido',
        'descricao': 'Descrição'
    }
    
    # 3. Formatação de valores monetários
    column_formatters = {
        'valor': formatar_moeda,
    }
    
    # 4. Busca e Filtros
    column_searchable_list = ['tipo', 'metodo_pagamento']
    column_filters = ['tipo', 'metodo_pagamento', 'data_movimento', 'caixa']
    column_default_sort = ('data_movimento', True)
    
    # 5. Choices para tipos e métodos
    form_choices = {
        'tipo': [
            ('venda', 'Venda'),
            ('devolucao', 'Devolução'),
            ('sangria', 'Sangria'),
            ('suprimento', 'Suprimento')
        ],
        'metodo_pagamento': [
            ('dinheiro', 'Dinheiro'),
            ('pix', 'PIX'),
            ('cartao_debito', 'Cartão Débito'),
            ('cartao_credito', 'Cartão Crédito')
        ]
    }
