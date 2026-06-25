from flask import Blueprint, render_template
from extensions import admin as flask_admin, db, admin_required
from worktime.models import Register, AuthorizedDevice, PointManagement