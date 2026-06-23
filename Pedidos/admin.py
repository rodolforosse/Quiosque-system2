# produtos/admin.py
from Usuarios.admin import SecureModelView
from Pedidos.models import Orders

# Formatador personalizado para exibir o valor em formato de Real (R$) na tabela do Admin
def formatar_moeda(view, context, model, name):
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
        'created_at': 'Data/Hora'
    }

    # 3. Filtros, Buscas e Ordenação Padrão
    column_searchable_list = ['order_id', 'coupon', 'observation'] # Campos com barra de busca
    column_filters = ['status', 'delivery', 'created_at']         # Filtros rápidos na lateral/topo
    column_default_sort = ('id', True)                             # Ordena trazendo os mais novos primeiro

    # 4. Customização de Formulário de Edição
    # Define quais campos o administrador PODE alterar ao clicar em editar
    form_columns = ['status', 'observation']
    
    # Define as opções de escolha para o campo Status no formulário do Admin
    form_choices = {
        'status': [
            ('R', 'Realizado'),
            ('EP', 'Em Preparação'),
            ('PR', 'Pronto p/ Retirada'),
            ('F', 'Finalizado'),
            ('C', 'Cancelado')
        ]
    }
