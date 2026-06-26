# Caixa/models.py
from datetime import datetime
from extensions import db

class Caixa(db.Model):
    """
    Modelo de Caixa para gerenciar abertura, fechamento e movimentações
    Rastreia todas as transações monetárias do ponto de venda
    """
    __tablename__ = 'caixa'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Datas de operação
    data_abertura = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_fechamento = db.Column(db.DateTime, nullable=True)
    
    # Valores
    valor_inicial = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    valor_vendas = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    valor_devolucoes = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    valor_final = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='aberto', nullable=False)  # aberto, fechado
    
    # Relacionamento com usuário que abriu/fechou
    user_abertura_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='RESTRICT'), nullable=False)
    user_abertura = db.relationship('User', foreign_keys=[user_abertura_id], backref=db.backref('caixas_abertos', lazy=True))
    
    user_fechamento_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='RESTRICT'), nullable=True)
    user_fechamento = db.relationship('User', foreign_keys=[user_fechamento_id], backref=db.backref('caixas_fechados', lazy=True))
    
    # Observações
    observacoes = db.Column(db.Text, default="", nullable=False)
    
    def __repr__(self):
        return f"<Caixa {self.id} - {self.status}>"
    
    @property
    def total_operacoes(self):
        """Valor total de operações (vendas - devoluções)"""
        return float(self.valor_vendas) - float(self.valor_devolucoes)
    
    @property
    def diferenca(self):
        """Diferença entre valor esperado e valor informado no fechamento"""
        esperado = float(self.valor_inicial) + self.total_operacoes
        return float(self.valor_final) - esperado if self.valor_final else 0


class MovimentacaoCaixa(db.Model):
    """
    Rastreia cada movimentação individual de caixa
    Integrada com Orders para auditoria
    """
    __tablename__ = 'movimentacao_caixa'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relacionamento com Caixa
    caixa_id = db.Column(db.Integer, db.ForeignKey('caixa.id', ondelete='CASCADE'), nullable=False)
    caixa = db.relationship('Caixa', backref=db.backref('movimentacoes', cascade='all, delete-orphan', lazy=True))
    
    # Relacionamento com Pedido (opcional - nem toda movimentação é um pedido)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=True)
    order = db.relationship('Orders', backref=db.backref('movimentacoes_caixa', lazy=True))
    
    # Tipo de movimentação
    tipo = db.Column(db.String(50), nullable=False)  # venda, devolucao, sangria, suprimento
    
    # Valores
    valor = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    
    # Método de pagamento
    metodo_pagamento = db.Column(db.String(50), nullable=False)  # dinheiro, pix, cartao_debito, cartao_credito
    
    # Timestamps
    data_movimento = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Usuário que executou
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='RESTRICT'), nullable=False)
    user = db.relationship('User', backref=db.backref('movimentacoes', lazy=True))
    
    # Observações
    descricao = db.Column(db.Text, default="", nullable=False)
    
    def __repr__(self):
        return f"<MovimentacaoCaixa {self.tipo} - R$ {self.valor}>"
