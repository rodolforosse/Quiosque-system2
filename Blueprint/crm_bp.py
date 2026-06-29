# crm/__init__.py
from flask import Blueprint, render_template
from extensions import admin as flask_admin, db


# Blueprint para futuras rotas CRM
crm_bp = Blueprint('crm', __name__)

