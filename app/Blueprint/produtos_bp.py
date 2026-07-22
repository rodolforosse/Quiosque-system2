from flask import Blueprint, render_template
from app.extensions import admin_required
from app.models import Products

# Cria o blueprint de produtos
produtos_bp = Blueprint('produtos', __name__)

produtos_bp.menu_items = [
    {
        'key': 'produtos.vitrine_publica',
        'name': 'Cadápio',
        'icon': 'solid fa-utensils',
        'order': 30,  # Ficará abaixo de pedidos
        'children': []
    }
]

# 1. ROTA PÚBLICA: Página Inicial
@produtos_bp.route('/')
@admin_required()
def index_publico():
    return render_template('site/index.html')

# 2. ROTA PÚBLICA: Vitrine de Produtos (ex: http://127.0.01/produtos)
@produtos_bp.route('/produtos')
@admin_required()
def vitrine_publica():
    # Busca todos os produtos salvos no banco de dados SQLite
    lista_de_produtos = Products.query.all()
    # Envia a lista para dentro do arquivo HTML mapeado
    return render_template('site/produtos.html', produtos=lista_de_produtos)

