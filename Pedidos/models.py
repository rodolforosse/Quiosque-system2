# produtos/modelos.py
from datetime import datetime
from extensions import db

class Orders(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento com Customers (PROTECT -> RESTRICT)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False)
    customer = db.relationship('Customers', backref=db.backref('clientes', lazy='dynamic'))
    
    # Campos de Texto e Detalhes
    discount = db.Column(db.String(50), default="", nullable=False)
    coupon = db.Column(db.String(50), default="", nullable=False)
    observation = db.Column(db.String(50), default="", nullable=False)
    
    # Escolhas (choices) gerenciadas na camada de formulário/aplicação
    delivery = db.Column(db.String(20), nullable=False) # balcao, ifood, whatsapp, etc.
    status = db.Column(db.String(20), nullable=False)   # R, EP, PR, F, C
    
    # Código do Pedido Sequencial (Garantido por Evento de banco abaixo)
    order_id = db.Column(db.Integer, unique=True, nullable=False)
    
    # Valores Monetários
    total_value = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)

    def __repr__(self):
        return f"<Order {self.order_id} - Status: {self.status}>"


# EVENTO EXCLUSIVO DO FLASK PARA GERAR O NÚMERO DO PEDIDO COM SEGURANÇA (SELECT FOR UPDATE)
@db.event.listens_for(Orders, 'before_insert')
def gerar_numero_pedido(mapper, connection, target):
    """
    Roda automaticamente antes de salvar um novo pedido no banco de dados.
    Equivale ao 'with transaction.atomic()' e 'select_for_update()' do Django.
    """
    if not target.order_id:
        NUMERO_INICIAL = 1000000
        
        # Cria uma query isolada usando a conexão atual e aplica o lock de linha (with_for_update)
        # Isso impede que outras requisições leiam o último pedido até que este seja salvo
        ultimo_pedido = (
            db.session.query(Orders)
            .with_for_update()
            .order_by(Orders.id.desc())
            .first()
        )
        
        if ultimo_pedido and ultimo_pedido.order_id:
            target.order_id = ultimo_pedido.order_id + 1
        else:
            target.order_id = NUMERO_INICIAL


class OrderItems(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    
    # Chave estrangeira para o Pedido (Com Cascade total na deleção)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    order = db.relationship('Orders', backref=db.backref('itens', cascade='all, delete-orphan', lazy=True))
    
    # Chave estrangeira para o Produto (Ajuste 'products.id' se sua tabela de produtos tiver outro nome no banco)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    product = db.relationship('Products', backref=db.backref('pedido_itens', lazy=True))
    
    # Quantidade e Valores Monetários
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<OrderItem: {self.quantity}x Produto ID {self.product_id} no Pedido ID {self.order_id}>"

    @property
    def total_price(self):
        """Retorna o valor total deste item (Quantidade x Preço Unitário)"""
        if self.quantity and self.unit_price:
            return self.quantity * self.unit_price
        return 0.00


