from flask import Blueprint, render_template
from extensions import admin_required
from sqlalchemy.orm import joinedload
from Pedidos.admin import OrdersAdminView
from Pedidos.models import Orders, OrderItems

# Cria o blueprint de produtos
pedidos_bp = Blueprint('pedidos', __name__)

pedidos_bp.menu_items = [
    {
        'key': 'pedidos.create_view',
        'name': 'Pedidos',
        'icon': 'bell-concierge',
        'order': 10,  # Ficará no topo
        'children': []
    }

]



@pedidos_bp.route('/pedidos')
@admin_required()
def create_view():
    # Carrega todos os pedidos trazendo os dados do cliente acoplados na mesma consulta
    pedidos = Orders.query.options(joinedload(Orders.customer)).order_by(Orders.id.desc()).all()
    
    return render_template('site/pedidos.html', pedidos=pedidos)

