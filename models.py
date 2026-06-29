import uuid
from datetime import datetime
from flask_security import UserMixin, RoleMixin
from extensions import db

class AuthorizedDevice(db.Model):
    __tablename__ = 'authorized_device'

    id = db.Column(db.Integer, primary_key=True)
    
    nome = db.Column(db.String(100), nullable=False)
    
    # Campo UUID gerado automaticamente. O parâmetro default=uuid.uuid4 
    # garante que um novo token seja gerado em cada inserção.
    identificador_unico = db.Column(
        db.String(36), 
        default=lambda: str(uuid.uuid4()), 
        unique=True, 
        nullable=False
    )
    
    # IP Estático mapeado como string (IPv4/IPv6 ocupam até 45 caracteres)
    ip_estatico = db.Column(db.String(45), nullable=True)
    
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AuthorizedDevice {self.nome} - {self.identificador_unico}>"


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


class Categories(db.Model):
  __tablename__ = 'categories'
  
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(20), nullable=False, unique=True)

  # CORREÇÃO: O back_populates agora aponta para o nome correto da propriedade singular ('category')
  products = db.relationship('Products', back_populates='category', lazy='dynamic')

  # Padrão universal do Flask para logs e depuração no terminal
  def __repr__(self) -> str:
    return f"{self.name}"


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


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    is_staff = db.Column(db.Boolean(), default=False)
    is_superuser = db.Column(db.Boolean(), default=False)
    
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


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


class ManageRecords(db.Query):
    """Manager customizado (Query Class) com métodos de filtro facilitados"""
    
    def entry(self):
        """Retorna todos os registros de entrada"""
        return self.filter_by(tipo_marcacao='E')

    def exit(self):
        """Retorna todos os registros de saída"""
        return self.filter_by(tipo_marcacao='S')


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


class Orders(db.Model):
  __tablename__ = 'orders'

  id = db.Column(db.Integer, primary_key=True)
  
  created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
  
  # Relacionamento com a tabela de Clientes (Chave estrangeira no plural)
  customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False)
  
  # Alterado o backref para 'pedidos' para fazer mais sentido semântico (Ex: cliente.pedidos)
  customer = db.relationship('Customers', backref=db.backref('pedidos', lazy='dynamic'))
  
  # CORREÇÃO 2: Alterado de String(50) para Numeric(10, 2) para permitir cálculos reais de desconto
  discount = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
  
  coupon = db.Column(db.String(50), default="", nullable=False)
  observation = db.Column(db.String(50), default="", nullable=False)
  
  # Escolhas (choices) gerenciadas na camada de formulário/aplicação
  delivery = db.Column(db.String(20), nullable=False) # balcao, ifood, whatsapp, etc.
  status = db.Column(db.String(20), nullable=False)   # R, EP, PR, F, C
  
  # Código do Pedido Sequencial (Garantido por Evento de banco)
  order_id = db.Column(db.Integer, unique=True, nullable=False)
  
  # Valores Monetários armazenados com precisão decimal
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


class OrderItems(db.Model):
  __tablename__ = 'order_items'

  id = db.Column(db.Integer, primary_key=True)
  
  # Chaves estrangeiras que apontam para as tabelas físicas do banco (Essas nunca quebram!)
  order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
  
  quantity = db.Column(db.Integer, nullable=False, default=1)
  unit_price = db.Column(db.Numeric(10, 2), nullable=False)

  # Relacionamento com a classe de cabeçalho do mesmo Blueprint (Orders)
  order = db.relationship('Orders', backref=db.backref('itens', cascade='all, delete-orphan', lazy=True))

  product = db.relationship('Products', foreign_keys=[product_id], backref=db.backref('order_items', lazy=True))


class PointManagement(db.Model):
    __tablename__ = 'point_management'

    id = db.Column(db.Integer, primary_key=True)

    # Relacionamento com o Registro Original (SET_NULL)
    # unique=True garante a regra 'unique_together = ['registro_ponto']'
    registro_ponto_id = db.Column(db.Integer, db.ForeignKey('register.id', ondelete='SET NULL'), unique=True, nullable=True)
    registro_ponto = db.relationship('Register', backref=db.backref('gerenciamentos', uselist=False))

    # Identificação do Funcionário (PROTECT -> RESTRICT)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='RESTRICT'), nullable=False)
    funcionario = db.relationship('Employees', backref=db.backref('gerenciamento_pontos', lazy='dynamic'))

    # Controle de Classificação (Com Index para acelerar buscas)
    classificacao = db.Column(db.String(20), default='NORMAL', index=True, nullable=False)

    # Campos de Ajuste
    data_hora_ajustada = db.Column(db.DateTime, nullable=True)
    justificativa_ajuste = db.Column(db.Text, nullable=True) # Text mapeia para TEXT/LONGTEXT no banco

    # Auditoria de Aprovação (Workflow)
    auditado_por_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='RESTRICT'), nullable=True)
    auditado_por = db.relationship('User', backref=db.backref('pontos_auditados', lazy='dynamic'))
    
    data_hora_auditoria = db.Column(db.DateTime, nullable=True)

    # Metadados do Sistema
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        horario = self.data_hora_ajustada or (self.registro_ponto.data_hora_servidor if self.registro_ponto else 'Inclusão Manual')
        return f"<PointManagement {self.funcionario} - {horario} [{self.classificacao}]>"

    @property
    def horario_efetivo(self):
        """Retorna o horário real que deve ser computado na folha de pagamento"""
        if self.classificacao in ['NORMAL', 'DIVERGENCIA', 'INCONSISTENCIA']:
            return self.registro_ponto.data_hora_servidor if self.registro_ponto else None
        elif self.classificacao == 'ABONADO':
            return self.data_hora_ajustada
        return None


class Register(db.Model):
    __tablename__ = 'register'

    # Vincula o seu manager customizado aqui
    query_class = ManageRecords

    id = db.Column(db.Integer, primary_key=True)

    # Identificação (Chaves Estrangeiras)
    # models.PROTECT é feito via RESTRICT no banco de dados para impedir a exclusão
    funcionario_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='RESTRICT'), nullable=False)
    funcionario = db.relationship('Employees', backref=db.backref('batidas_ponto', lazy='dynamic'))

    dispositivo_id = db.Column(db.Integer, db.ForeignKey('authorized_device.id', ondelete='RESTRICT'), nullable=False)
    dispositivo = db.relationship('AuthorizedDevice', backref=db.backref('registros', lazy='dynamic'))

    # Dados da Jornada (Portaria 671)
    # BigIntegerField vira db.BigInteger. unique=True cuida do 'unique_together = ['nsr']'
    nsr = db.Column(db.BigInteger, unique=True, nullable=False) 
    tipo_marcacao = db.Column(db.String(1), nullable=False) # 'E' ou 'S' (validação feita na rota/view)

    # Horários (Integridade)
    data_hora_servidor = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_hora_dispositivo = db.Column(db.DateTime, nullable=False)

    # Segurança e auditoria
    hash_integridade = db.Column(db.String(64), nullable=False)
    ip_origem = db.Column(db.String(45), nullable=False) # IPv4 ou IPv6 ocupam até 45 caracteres
    
    # Coordenadas geográficas de alta precisão
    latitude = db.Column(db.Numeric(22, 16), nullable=True)
    longitude = db.Column(db.Numeric(22, 16), nullable=True)

    def __repr__(self):
        return f"<Register {self.funcionario_id} - {self.data_hora_servidor}>"

    # Substitutos para os @property do Django (Métodos do modelo no Flask)
    def last_entry(self):
        """Retorna a última marcação de entrada do funcionário"""
        return Register.query.filter_by(
            funcionario_id=self.funcionario_id, 
            tipo_marcacao='E'
        ).order_by(Register.data_hora_servidor.desc()).first()

    def last_exit(self):
        """Retorna a última marcação de saída do funcionário"""
        return Register.query.filter_by(
            funcionario_id=self.funcionario_id, 
            tipo_marcacao='S'
        ).order_by(Register.data_hora_servidor.desc()).first()


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    permissions = db.Column(db.JSON, nullable=True) 

    def __str__(self):
        return self.name


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