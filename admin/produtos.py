# produtos/admin.py
from admin.usuarios import SecureModelView
from models import Products, Categories

class CategoryAdminView(SecureModelView):
    column_list = ['id', 'name']
    column_labels = {'id': 'ID', 'name': 'Categoria'}

    def __init__(self, session, **kwargs):
        super(CategoryAdminView, self).__init__(Categories, session, **kwargs)


class ProductsAdminView(SecureModelView):
    # 1. Ajuste na listagem de colunas da tabela do admin
    # Troque 'category_ref' por 'category'
    column_list = ['id', 'name', 'price', 'category', 'is_active']
    
    # 2. Ajuste nos rótulos amigáveis (cabeçalhos em português)
    column_labels = {
        'id': 'ID',
        'name': 'Nome do Produto',
        'price': 'Preço',
        'category': 'Categoria',  # <-- Ajustado de category_ref para category
        'is_active': 'Ativo',
        'description': 'Descrição',
        'created_at': 'Criado em',
        'updated_at': 'Atualizado em'
    }

    # 3. Ajuste nos filtros rápidos ou barra de buscas se houver
    # Garanta que use apenas propriedades reais do seu modelo (como 'category.name')
    column_searchable_list = ['name']
    column_filters = ['price','is_active', 'category.name'] 
    
    # 4. Ajuste nas colunas do formulário de inserção/edição
    form_columns = ['name', 'price', 'description', 'category', 'is_active']

    def __init__(self, session, **kwargs):
        super(ProductsAdminView, self).__init__(Products, session, **kwargs)