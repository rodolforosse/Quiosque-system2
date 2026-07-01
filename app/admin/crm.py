# crm/admin.py
from .usuarios import SecureModelView
from app.models import Customers, Employees, Suppliers

class CustomersAdminView(SecureModelView):
    """
    Painel de gerenciamento de Clientes/Consumidores
    Suporta Pessoa Física (PF) e Pessoa Jurídica (PJ)
    """
    # 1. Configurações de Permissões CRUD
    can_create = True
    can_edit = True
    can_delete = False  # Nunca deletar clientes por histórico
    can_view_details = True
    
    # 2. Configurações de Exibição
    column_list = ['id', 'name', 'type', 'email', 'phone', 'ativo', 'data_cadastro']
    column_labels = {
        'id': 'ID',
        'name': 'Nome/Razão Social',
        'type': 'Tipo',
        'document': 'CPF/CNPJ',
        'email': 'E-mail',
        'phone': 'Telefone',
        'address': 'Endereço',
        'district': 'Bairro',
        'ativo': 'Ativo',
        'data_cadastro': 'Data Cadastro'
    }
    
    # 3. Busca e Filtros
    column_searchable_list = ['name', 'email', 'phone', 'document']
    column_filters = ['type', 'ativo', 'data_cadastro']
    column_default_sort = ('data_cadastro', True)  # Mais recentes primeiro
    
    # 4. Formulário de Edição
    form_columns = ['name', 'type', 'document', 'email', 'phone', 'address', 'district', 'ativo']
    
    # 5. Choices para o campo 'type'
    form_choices = {
        'type': [
            ('PF', 'Pessoa Física'),
            ('PJ', 'Pessoa Jurídica')
        ]
    }

    def __init__(self, session, **kwargs):
        super(CustomersAdminView, self).__init__(Customers, session, **kwargs)


class EmployeesAdminView(SecureModelView):
    """
    Painel de gerenciamento de Funcionários/Colaboradores
    Vinculado ao usuário do sistema para autenticação
    """
    # 1. Configurações de Permissões CRUD
    can_create = True
    can_edit = True
    can_delete = False  # Manter histórico de funcionários
    can_view_details = True
    
    # 2. Configurações de Exibição
    column_list = ['id', 'first_name', 'surname', 'user', 'cargo', 'data_contratacao']
    column_labels = {
        'id': 'ID',
        'first_name': 'Primeiro Nome',
        'surname': 'Sobrenome',
        'user': 'Usuário Sistema',
        'cpf': 'CPF',
        'cargo': 'Cargo',
        'endereco': 'Endereço',
        'data_contratacao': 'Data Contratação',
        'data_demissao': 'Data Demissão',
        'salario': 'Salário',
        'telefone': 'Telefone'
    }
    
    # 3. Busca e Filtros
    column_searchable_list = ['first_name', 'surname', 'cpf', 'cargo']
    column_filters = ['cargo', 'data_contratacao']
    column_default_sort = ('first_name', False)
    
    # 4. Formulário de Edição
    form_columns = [
        'user', 'first_name', 'surname', 'cpf', 
        'cargo', 'endereco', 'telefone',
        'data_contratacao', 'data_demissao', 'salario'
    ]

    def __init__(self, session, **kwargs):
        super(EmployeesAdminView, self).__init__(Employees, session, **kwargs)

class SuppliersAdminView(SecureModelView):
    """
    Painel de gerenciamento de Fornecedores
    Para gestão de insumos e matérias-primas
    """
    # 1. Configurações de Permissões CRUD
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True
    
    # 2. Configurações de Exibição
    column_list = ['id', 'nome', 'contato', 'telefone', 'email', 'created_at']
    column_labels = {
        'id': 'ID',
        'nome': 'Nome Fornecedor',
        'contato': 'Contato Principal',
        'telefone': 'Telefone',
        'email': 'E-mail',
        'endereco': 'Endereço',
        'created_at': 'Cadastrado em',
        'updated_at': 'Atualizado em'
    }
    
    # 3. Busca e Filtros
    column_searchable_list = ['nome', 'email', 'telefone', 'contato']
    column_filters = ['created_at']
    column_default_sort = ('nome', False)
    
    # 4. Formulário de Edição
    form_columns = ['nome', 'contato', 'telefone', 'email', 'endereco']

    def __init__(self, session, **kwargs):
        super(SuppliersAdminView, self).__init__(Suppliers, session, **kwargs)
