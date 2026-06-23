# produtos/modelos.py
from datetime import datetime
from extensions import db

class Orders(db.Model):
    __tablename__ = 'Orders'

