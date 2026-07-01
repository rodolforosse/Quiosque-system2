from app.extensions import flask_admin, db
from .caixa import(
    CaixaAdminView,
    MovimentacaoCaixaAdminView
)
from .crm import (
    CustomersAdminView, 
    EmployeesAdminView, 
    SuppliersAdminView
)
from .pedidos import (
    OrdersAdminView,
    OrderItemsAdminView
)
from .produtos import (
    CategoryAdminView,
    ProductsAdminView
)
from .usuarios import (
    RoleAdminView,
    UserAdminView
)

# Registra as views de caixa em admin
flask_admin.add_view(CaixaAdminView(db.session, name="Caixadb", category="Financeiro"))
flask_admin.add_view(MovimentacaoCaixaAdminView(db.session, name="Movimentações", category="Financeiro"))

# Registra as views do crm em admin
flask_admin.add_view(CustomersAdminView(db.session, name="Clientes", category="CRM"))
flask_admin.add_view(EmployeesAdminView(db.session, name="Funcionários", category="CRM"))
flask_admin.add_view(SuppliersAdminView(db.session, name="Fornecedores", category="CRM"))

# Registra as views de Pedidos em admin
flask_admin.add_view(OrdersAdminView(db.session, name="Pedidos", category="Vendas"))
flask_admin.add_view(OrderItemsAdminView(db.session, name="Itens dos Pedidos", category="Vendas"))

# Registra as views de Produtos em admin
flask_admin.add_view(CategoryAdminView(db.session, name="Categorias", category="Catálogo"))
flask_admin.add_view(ProductsAdminView(db.session, name="Produtos", category="Catálogo"))

# Adiciona o gerenciamento de Usuários e Grupos ao menu do Admin
flask_admin.add_view(UserAdminView(db.session, name="Usuários", category="Segurança"))
flask_admin.add_view(RoleAdminView(db.session, name="Grupos/Roles", category="Segurança"))
