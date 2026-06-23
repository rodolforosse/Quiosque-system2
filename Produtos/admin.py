# produtos/admin.py
from Usuarios.admin import SecureModelView
from Produtos.models import Products, Category

class CategoryAdminView(SecureModelView):
    column_list = ['id', 'name']
    column_labels = {'id': 'ID', 'name': 'Categoria'}

    def __init__(self, session, **kwargs):
        super(CategoryAdminView, self).__init__(Category, session, **kwargs)


class ProductsAdminView(SecureModelView):
    # Oculta campos automáticos de IDs e Datas no formulário de criação
    form_excluded_columns = ['id', 'created_at', 'updated_at']
    
    # Define a ordenação padrão por Nome (Equivalente ao ordering = ['name'] do Django)
    column_default_sort = ('name', False) # False significa ordem Ascendente (A-Z)
    
    # Define as colunas visíveis na listagem principal do painel
    column_list = ['id', 'name', 'price', 'is_active', 'category_ref', 'created_at']
    
    # Mapeamento do verbose_name do Django para o Flask-Admin
    column_labels = {
        'id': 'ID',
        'name': 'Nome',
        'price': 'Preço',
        'is_active': 'Ativo',
        'description': 'Descrição',
        'created_at': 'Criado em',
        'updated_at': 'Atualizado em',
        'category_ref': 'Categoria' # Lese a referência do relacionamento backref
    }
    
    column_searchable_list = ['name']
    column_filters = ['price', 'is_active', 'category_ref.name']

    def __init__(self, session, **kwargs):
        super(ProductsAdminView, self).__init__(Products, session, **kwargs)
