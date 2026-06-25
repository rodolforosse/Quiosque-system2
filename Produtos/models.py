# produtos/modelos.py
from datetime import datetime
from extensions import db

class Categories(db.Model):
  __tablename__ = 'categories'
  
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(20), nullable=False, unique=True)

  # CORREÇÃO: O back_populates agora aponta para o nome correto da propriedade singular ('category')
  products = db.relationship('Products', back_populates='category', lazy='dynamic')

  # Padrão universal do Flask para logs e depuração no terminal
  def __repr__(self) -> str:
    return f"{self.name}"


class Products(db.Model):
  __tablename__ = 'products'
  
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(100), nullable=False)
  price = db.Column(db.Float, nullable=False)
  is_active = db.Column(db.Boolean, default=True, nullable=False)
  description = db.Column(db.Text, nullable=True, default="")
  created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
  
  # 1. ADICIONADO: A coluna de Chave Estrangeira física necessária para criar o vínculo no banco
  category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
  
  # 2. CORREÇÃO: Relacionamento ajustado para o singular ('category') e espelhado com o back_populates correto
  category = db.relationship('Categories', back_populates='products')

  def __repr__(self) -> str:
    return f"{self.name}"
