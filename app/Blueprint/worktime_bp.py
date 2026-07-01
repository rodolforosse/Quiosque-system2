from flask import Blueprint, render_template
from app.extensions import admin as flask_admin, db, admin_required
from app.models import Register, AuthorizedDevice, PointManagement