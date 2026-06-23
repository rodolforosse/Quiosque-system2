from flask import Blueprint, render_template
from extensions import admin as flask_admin, db, admin_required
from Caixa.admin import CaixaAdminView
from Caixa.modelos import Caixa

# Cria o blueprint de produtos
produtos_bp = Blueprint('caixa', __name__)

produtos_bp.menu_items = [
    {
        'key': 'caixa.create_view',
        'name': 'Caixa',
        'icon': 'calculator',
        'order': 10,  # Ficará no topo
        'children': []
    }

]

# 1. ROTA PÚBLICA: Vitrine de Produtos (ex: http://127.0.01/produtos)
@produtos_bp.route('/caixa')
@admin_required()
def create_view():
    # Busca todos os produtos salvos no banco de dados SQLite
    lista_de_produtos = Caixa.query.all()
    # Envia a lista para dentro do arquivo HTML mapeado
    return render_template('site/caixa.html', dashboards=None)

# Usamos o 'flask_admin' registrar a View
flask_admin.add_view(CaixaAdminView(db.session))

