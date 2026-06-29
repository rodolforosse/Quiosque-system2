# Pedidos/admin.py
from extensions import admin as flask_admin, db
from admin.usuarios import SecureModelView
from models import Orders, OrderItems

# Formatador personalizado para exibir o valor em formato de Real (R$) na tabela do Admin
def formatar_moeda(model, name):
    valor = getattr(model, name)
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor else "R$ 0,00"

class OrdersAdminView(SecureModelView):
    """
    Painel administrativo customizado para gerenciamento e auditoria de Pedidos.
    """
    # 1. Configurações de Permissões Básicas (CRUD)
    can_create = False  # Pedidos geralmente são gerados pelo cliente/sistema, não criados manualmente no admin
    can_edit = True     # Permite alterar o status ou adicionar observações
    can_delete = False  # Pedidos nunca devem ser deletados por integridade fiscal (use o status Cancelado)
    can_view_details = True # Ativa a página de visualização detalhada de cada pedido
    
    # 2. Configurações de Exibição de Colunas
    column_list = [
        'order_id', 'customer', 'delivery', 'status', 'total_value', 'created_at'
    ]
    
    # Rótulos amigáveis para os cabeçalhos da tabela (Equivale ao verbose_name do Django)
    column_labels = {
        'order_id': 'Código do Pedido',
        'customer': 'Cliente',
        'delivery': 'Canal de Venda/Entrega',
        'status': 'Status Atual',
        'total_value': 'Valor Total',
        'discount': 'Desconto',
        'coupon': 'Cupom',
        'observation': 'Observação',
        'created_at': 'Data/Hora',
        'updated_at': 'Última Atualização'
    }

    # 3. Formatação de valores monetários
    column_formatters = {
        'total_value': formatar_moeda,
    }

    # 4. Filtros, Buscas e Ordenação Padrão
    column_searchable_list = ['order_id', 'coupon', 'observation'] # Campos com barra de busca
    column_filters = ['status', 'delivery', 'created_at']         # Filtros rápidos na lateral/topo
    column_default_sort = ('id', True)                             # Ordena trazendo os mais novos primeiro

    # 5. Customização de Formulário de Edição
    # Define quais campos o administrador PODE alterar ao clicar em editar
    form_columns = ['status', 'discount', 'coupon', 'observation']
    
    # Define as opções de escolha para o campo Status no formulário do Admin
    form_choices = {
        'status': [
            ('R', 'Realizado'),
            ('EP', 'Em Preparação'),
            ('PR', 'Pronto p/ Retirada'),
            ('F', 'Finalizado'),
            ('C', 'Cancelado')
        ],
        'delivery': [
            ('balcao', 'Balcão'),
            ('ifood', 'iFood'),
            ('whatsapp', 'WhatsApp'),
            ('delivery', 'Delivery Próprio')
        ]
    }

    def __init__(self, session, **kwargs):
        super(OrdersAdminView, self).__init__(Orders, session, **kwargs)

class OrderItemsAdminView(SecureModelView):
    """
    Painel administrativo para gerenciar itens de pedidos individuais
    Controla produtos adicionados aos pedidos
    """
    # 1. Configurações de Permissões CRUD
    can_create = False  # Itens devem ser criados via interface de pedidos
    can_edit = False    # Edições de itens devem ser refletidas com cálculo de totais
    can_delete = False  # Histórico fiscal
    can_view_details = True
    
    # 2. Configurações de Exibição
    column_list = [
        'id', 'order', 'product', 'quantity', 'unit_price', 'created_at'
    ]
    
    column_labels = {
        'id': 'ID',
        'order': 'Pedido',
        'product': 'Produto',
        'quantity': 'Quantidade',
        'unit_price': 'Preço Unitário',
        'total_price': 'Total Item',
        'created_at': 'Criado em'
    }
    
    # 3. Formatação de colunas
    column_formatters = {
        'unit_price': formatar_moeda,
    }
    
    # 4. Busca e Filtros
    column_searchable_list = ['product.name', 'order.order_id']
    column_filters = ['order', 'product']
    column_default_sort = ('id', True)
    
    # 5. Apenas visualização
    form_columns = []

    def __init__(self, session, **kwargs):
        super(OrderItemsAdminView, self).__init__(OrderItems, session, **kwargs)

flask_admin.add_view(OrdersAdminView(Orders, db.session, name="Pedidos", category="Vendas"))
flask_admin.add_view(OrderItemsAdminView(OrderItems, db.session, name="Itens dos Pedidos", category="Vendas"))
