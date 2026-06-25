# worktime/models.py
import uuid
from datetime import datetime
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


class ManageRecords(db.Query):
    """Manager customizado (Query Class) com métodos de filtro facilitados"""
    
    def entry(self):
        """Retorna todos os registros de entrada"""
        return self.filter_by(tipo_marcacao='E')

    def exit(self):
        """Retorna todos os registros de saída"""
        return self.filter_by(tipo_marcacao='S')


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


