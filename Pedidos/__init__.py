from flask import Blueprint, render_template
from extensions import admin as flask_admin, db, admin_required
from Pedidos.admin import OrdersAdminView
from Pedidos.models import Orders

# Cria o blueprint de produtos
produtos_bp = Blueprint('dashboard', __name__)

produtos_bp.menu_items = [
    {
        'key': 'pedidos.create_view',
        'name': 'Pedidos',
        'icon': 'bell-concierge',
        'order': 10,  # Ficará no topo
        'children': []
    }

]

# 2. ROTA PÚBLICA: Vitrine de Produtos (ex: http://127.0.01/produtos)
@produtos_bp.route('/pedidos')
@admin_required()
def create_view():
    # Busca todos os produtos salvos no banco de dados SQLite
    lista_de_produtos = Orders.query.all()
    # Envia a lista para dentro do arquivo HTML mapeado
    return render_template('site/pedidos.html', pedidos=None)

# Usamos o 'flask_admin' registrar a View
flask_admin.add_view(OrdersAdminView(db.session))

