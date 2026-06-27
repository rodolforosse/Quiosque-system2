# Pedidos/__init__.py
from flask import Blueprint, render_template
from extensions import admin as flask_admin, db, admin_required
<<<<<<< HEAD
from Pedidos.admin import OrdersAdminView, OrderItemsAdminView
from Pedidos.models import Orders, OrderItems

# Registra as views de admin
flask_admin.add_view(OrdersAdminView(Orders, db.session, name="Pedidos", category="Vendas"))
flask_admin.add_view(OrderItemsAdminView(OrderItems, db.session, name="Itens do Pedido", category="Vendas"))

=======
from sqlalchemy.orm import joinedload
from Pedidos.admin import OrdersAdminView, OrdersItemsAdminView
from Pedidos.models import Orders, OrderItems

>>>>>>> dbfc2dc (Atualizacao do dia 27-06-2026)
# Cria o blueprint de pedidos
pedidos_bp = Blueprint('pedidos', __name__)

pedidos_bp.menu_items = [
    {
        'key': None,
        'name': 'Vendas',
        'icon': 'shopping-bag',
        'order': 30,  # Abaixo de Caixa
        'children': [
            {
                'key': 'pedidos.listar',
                'name': 'Pedidos',
                'icon': 'list'
            },
            {
                'key': 'pedidos.criar',
                'name': 'Novo Pedido',
                'icon': 'plus-circle'
            }
        ]
    }
]

# 1. ROTA: Listar Pedidos
@pedidos_bp.route('/pedidos')
@admin_required()
def listar():
    """
    Lista todos os pedidos com filtros e busca
    """
    # Filtragem pode ser expandida com query parameters
    pedidos = Orders.query.order_by(Orders.created_at.desc()).all()
    return render_template('site/pedidos.html', pedidos=pedidos)

<<<<<<< HEAD
# 2. ROTA: Criar Novo Pedido
@pedidos_bp.route('/pedidos/criar')
@admin_required()
def criar():
    """
    Interface para criar novo pedido (integrado com caixa)
    """
    return render_template('site/pedidos.html', modo='criar')
=======

flask_admin.add_view(OrdersAdminView(Orders, db.session, name="Pedidos", category="Vendas"))
flask_admin.add_view(OrdersItemsAdminView(OrderItems, db.session, name="Itens dos Pedidos", category="Vendas"))

>>>>>>> dbfc2dc (Atualizacao do dia 27-06-2026)
