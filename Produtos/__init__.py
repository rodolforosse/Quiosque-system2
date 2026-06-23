from flask import Blueprint, render_template
from extensions import admin as flask_admin, db, admin_required
from Produtos.admin import ProductsAdminView, CategoryAdminView
from Produtos.modelos import Products


flask_admin.add_view(CategoryAdminView(db.session, name="Categorias", category="Catálogo"))
flask_admin.add_view(ProductsAdminView(db.session, name="Produtos", category="Catálogo"))


# Cria o blueprint de produtos
produtos_bp = Blueprint('produtos', __name__)

produtos_bp.menu_items = [
    {
        'key': 'produtos.index_publico',
        'name': 'Página Inicial',
        'icon': 'home',
        'order': 10,  # Ficará no topo
        'children': []
    },
    {
        'key': None,
        'name': 'Catálogos',
        'icon': 'box',
        'order': 20,  # Ficará logo abaixo da página inicial
        'children': [
            {
                'key': 'produtos.vitrine_publica',
                'name': 'Ver Produtos',
                'icon': 'shopping-cart'
            }
        ]
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

