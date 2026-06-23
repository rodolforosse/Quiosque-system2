# produtos/modelos.py
from datetime import datetime
from extensions import db

class Category(db.Model):
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # name = models.CharField(max_length=20)
    name = db.Column(db.String(20), nullable=False, unique=True)

    # Relacionamento de 1 para Muitos (Equivalente ao reverse relation do Django)
    products = db.relationship('Products', backref='category_ref', lazy=True)

    def __str__(self) -> str:
        return self.name


class Products(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.Text, nullable=True, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Chave Estrangeira ligando ao ID da Categoria
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __str__(self) -> str:
        return self.name
