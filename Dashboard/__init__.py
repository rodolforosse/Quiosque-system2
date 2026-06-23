from flask import Blueprint, render_template
from extensions import admin as flask_admin, db, admin_required
from Dashboard.admin import DashAdminView
from Dashboard.modelos import Dashboard

# Cria o blueprint de produtos
produtos_bp = Blueprint('dashboard', __name__)

produtos_bp.menu_items = [
    {
        'key': 'dashboard.create_view',
        'name': 'Dashboard',
        'icon': 'chart-line',
        'order': 10,  # Ficará no topo
        'children': []
    }

]

# 1. ROTA PÚBLICA: Vitrine de Produtos (ex: http://127.0.01/produtos)
@produtos_bp.route('/dashboard')
@admin_required()
def create_view():
    # Busca todos os produtos salvos no banco de dados SQLite
    lista_de_produtos = Dashboard.query.all()
    # Envia a lista para dentro do arquivo HTML mapeado
    return render_template('site/dashboard.html', dashboards=None)

# Usamos o 'flask_admin' registrar a View
flask_admin.add_view(DashAdminView(db.session))

