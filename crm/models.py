from datetime import datetime
from extensions import db

class Customers(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(2), default='PF', nullable=False)
    document = db.Column(db.String(18), default="", nullable=False)
    
    # Contato
    email = db.Column(db.String(255), unique=True, nullable=True)
    phone = db.Column(db.String(20), default="", nullable=False)

    # Endereço
    address = db.Column(db.String(128), default="", nullable=False)
    district = db.Column(db.String(50), default="", nullable=False)
    
    # Controle e Métricas
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Customer {self.name}>"

    # Método utilitário para substituir o get_type_display() automático do Django
    @property
    def get_type_display(self):
        opcoes = {
            'PF': 'Pessoa Física',
            'PJ': 'Pessoa Jurídica'
        }
        return opcoes.get(self.type, self.type)


class Employees(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # onupdate atualiza o timestamp automaticamente sempre que a linha sofrer alteração
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    first_name = db.Column(db.String(40), default="", nullable=False)
    surname = db.Column(db.String(60), default="", nullable=False)
    
    # OneToOneField do Django vira uma ForeignKey com unique=True e uselist=False no Flask
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
    user = db.relationship('User', backref=db.backref('funcionario', uselist=False), lazy=True)
    
    cpf = db.Column(db.String(14), unique=True, nullable=True)
    endereco = db.Column(db.String(255), default="", nullable=False)
    cargo = db.Column(db.String(100), default="", nullable=False)
    
    data_contratacao = db.Column(db.Date, nullable=True)
    data_demissao = db.Column(db.Date, nullable=True)
    
    # DecimalField vira db.Numeric
    salario = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    telefone = db.Column(db.String(15), default="000000000000000", nullable=False)

    def __repr__(self):
        return f"<Employee {self.first_name} {self.surname}>"


class Suppliers(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    
    # Controle de datas automático
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Campos de dados do fornecedor
    nome = db.Column(db.String(255), nullable=False)
    contato = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), nullable=False)  # Flask usa String para e-mails
    endereco = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Supplier {self.nome}>"

