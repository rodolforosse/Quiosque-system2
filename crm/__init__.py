# crm/__init__.py
from flask import Blueprint, render_template
from extensions import admin as flask_admin, db
from crm.models import Customers, Employees, Suppliers
from crm.admin import CustomersAdminView, EmployeesAdminView, SuppliersAdminView

# Registra as views de admin
flask_admin.add_view(CustomersAdminView(Customers, db.session, name="Clientes", category="CRM"))
flask_admin.add_view(EmployeesAdminView(Employees, db.session, name="Funcionários", category="CRM"))
flask_admin.add_view(SuppliersAdminView(Suppliers, db.session, name="Fornecedores", category="CRM"))

# Blueprint para futuras rotas CRM
crm_bp = Blueprint('crm', __name__)
