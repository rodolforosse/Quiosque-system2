# Dashboard/__init__.py
from flask import Blueprint, render_template, request
from sqlalchemy import func
from app.extensions import db, admin_required
from datetime import datetime, timedelta
from app.models import Orders, Customers

# Cria o blueprint de dashboard
dashboard_bp = Blueprint('dashboard', __name__)

dashboard_bp.menu_items = [
    {
        'key': 'dashboard.index',
        'name': 'Dashboard',
        'icon': 'chart-line',
        'order': 5,  # Ficará no topo
        'children': []
    }
]

def get_date_range(periodo):
    """Retorna tuple (data_inicio, data_fim) baseado no período selecionado"""
    hoje = datetime.now()
    
    if periodo == 'hoje':
        return (hoje.replace(hour=0, minute=0, second=0), hoje.replace(hour=23, minute=59, second=59))
    
    elif periodo == 'ontem':
        ontem = hoje - timedelta(days=1)
        return (ontem.replace(hour=0, minute=0, second=0), ontem.replace(hour=23, minute=59, second=59))
    
    elif periodo == 'estemes':
        inicio = hoje.replace(day=1, hour=0, minute=0, second=0)
        return (inicio, hoje.replace(hour=23, minute=59, second=59))
    
    elif periodo == 'mespassado':
        primeiro_dia = (hoje.replace(day=1) - timedelta(days=1)).replace(day=1)
        ultimo_dia = hoje.replace(day=1) - timedelta(days=1)
        return (primeiro_dia, ultimo_dia.replace(hour=23, minute=59, second=59))
    
    elif periodo == 'esteano':
        inicio = hoje.replace(month=1, day=1, hour=0, minute=0, second=0)
        return (inicio, hoje.replace(hour=23, minute=59, second=59))
    
    elif periodo == 'anopassado':
        inicio = (hoje.replace(year=hoje.year-1, month=1, day=1, hour=0, minute=0, second=0))
        fim = (hoje.replace(year=hoje.year-1, month=12, day=31, hour=23, minute=59, second=59))
        return (inicio, fim)
    
    # Default: hoje
    return (hoje.replace(hour=0, minute=0, second=0), hoje.replace(hour=23, minute=59, second=59))


# 1. ROTA PÚBLICA: Dashboard (ex: http://127.0.0.1/dashboard)
@dashboard_bp.route('/dashboard')
@admin_required()
def index():
    """
    Dashboard com métricas em tempo real do sistema de vendas
    Integra dados de Pedidos, Clientes e Caixa
    """
    # 1. Configuração do Dropdown de Períodos
    periodos = {
        'hoje': 'Hoje',
        'ontem': 'Ontem',
        'estemes': 'Este mês',
        'mespassado': 'Mês passado',
        'esteano': 'Este ano',
        'anopassado': 'Ano passado',
        'personalizado': 'Personalizado'
    }
    
    # Captura o período selecionado na URL ou assume 'hoje' por padrão
    periodo_selecionado = request.args.get('periodo', 'hoje')
    
    # Obtém range de datas
    data_inicio, data_fim = get_date_range(periodo_selecionado)
    
    # 2. CÁLCULO DE MÉTRICAS PRINCIPAIS (com dados reais do banco)
    
    # Total de Faturamento
    total_faturamento = db.session.query(
        func.sum(Orders.total_value)
    ).filter(
        Orders.created_at >= data_inicio,
        Orders.created_at <= data_fim,
        Orders.status != 'C'  # Exclui pedidos cancelados
    ).scalar() or 0
    
    # Total de Pedidos
    total_pedidos = db.session.query(func.count(Orders.id)).filter(
        Orders.created_at >= data_inicio,
        Orders.created_at <= data_fim,
        Orders.status != 'C'
    ).scalar() or 0
    
    # Ticket Médio
    ticket_medio = float(total_faturamento) / total_pedidos if total_pedidos > 0 else 0
    
    # Total de Clientes Ativos
    total_clientes = db.session.query(func.count(Customers.id)).filter(
        Customers.ativo == True
    ).scalar() or 0
    
    # 3. DADOS DOS GRÁFICOS - Faturamento por Mês (últimos 5 meses)
    grafico_meses = []
    grafico_faturamento = []
    grafico_pedidos_qtd = []
    
    for i in range(4, -1, -1):  # Últimos 5 meses
        mes_data = datetime.now() - timedelta(days=30*i)
        mes_inicio = mes_data.replace(day=1, hour=0, minute=0, second=0)
        
        # Próximo mês
        if mes_data.month == 12:
            mes_fim = mes_data.replace(year=mes_data.year+1, month=1, day=1, hour=0, minute=0, second=0) - timedelta(seconds=1)
        else:
            mes_fim = mes_data.replace(month=mes_data.month+1, day=1, hour=0, minute=0, second=0) - timedelta(seconds=1)
        
        # Query para o mês
        faturamento_mes = db.session.query(
            func.sum(Orders.total_value)
        ).filter(
            Orders.created_at >= mes_inicio,
            Orders.created_at <= mes_fim,
            Orders.status != 'C'
        ).scalar() or 0
        
        pedidos_mes = db.session.query(func.count(Orders.id)).filter(
            Orders.created_at >= mes_inicio,
            Orders.created_at <= mes_fim,
            Orders.status != 'C'
        ).scalar() or 0
        
        grafico_meses.append(mes_data.strftime("%b"))
        grafico_faturamento.append(float(faturamento_mes))
        grafico_pedidos_qtd.append(pedidos_mes)
    
    # 4. Dados dos Gráficos Donut (Fileira 3)
    # Distribuição por Plataforma (entrega)
    plataformas_labels = ["Balcão", "iFood", "WhatsApp"]
    plataformas_valores = [
        db.session.query(func.count(Orders.id)).filter(Orders.delivery == 'balcao').scalar() or 0,
        db.session.query(func.count(Orders.id)).filter(Orders.delivery == 'ifood').scalar() or 0,
        db.session.query(func.count(Orders.id)).filter(Orders.delivery == 'whatsapp').scalar() or 0,
    ]
    
    # Distribuição por Status
    origem_labels = ["Realizado", "Em Prep.", "Pronto", "Finalizado"]
    origem_valores = [
        db.session.query(func.count(Orders.id)).filter(Orders.status == 'R').scalar() or 0,
        db.session.query(func.count(Orders.id)).filter(Orders.status == 'EP').scalar() or 0,
        db.session.query(func.count(Orders.id)).filter(Orders.status == 'PR').scalar() or 0,
        db.session.query(func.count(Orders.id)).filter(Orders.status == 'F').scalar() or 0,
    ]
    
    # Métodos de Pagamento (mock - será expandido)
    pagamento_labels = ["Dinheiro", "PIX", "Crédito", "Débito"]
    pagamento_valores = [25, 45, 20, 10]
    
    # Entrega
    entrega_labels = ["Balcão", "Delivery"]
    entrega_valores = [
        db.session.query(func.count(Orders.id)).filter(Orders.delivery.in_(['balcao'])).scalar() or 0,
        db.session.query(func.count(Orders.id)).filter(Orders.delivery.in_(['ifood', 'whatsapp', 'delivery'])).scalar() or 0,
    ]
    
    # 5. Gráficos de Categorias (mock - será expandido com relação Products)
    categorias_labels = ["Eletrônicos", "Roupas", "Alimentos", "Acessórios"]
    categorias_valores = [8500.00, 4200.00, 2730.50, 1200.00]
    
    # 6. Envio de todas as variáveis para o Template HTML
    return render_template(
        'site/dashboard.html',
        # Configurações do Filtro
        periodos=periodos,
        periodo_selecionado=periodo_selecionado,
        
        # Cartões de Métricas Principais
        faturamento=float(total_faturamento),
        total_pedidos=total_pedidos,
        ticket_medio=round(ticket_medio, 2),
        total_clientes=total_clientes,
        
        # Dados dos Gráficos de Linha e Barra
        grafico_meses=grafico_meses,
        grafico_faturamento=grafico_faturamento,
        grafico_pedidos_qtd=grafico_pedidos_qtd,
        categorias_labels=categorias_labels,
        categorias_valores=categorias_valores,
        
        # Dados Obrigatórios dos Donuts
        plataformas_labels=plataformas_labels,
        plataformas_valores=plataformas_valores,
        origem_labels=origem_labels,
        origem_valores=origem_valores,
        pagamento_labels=pagamento_labels,
        pagamento_valores=pagamento_valores,
        entrega_labels=entrega_labels,
        entrega_valores=entrega_valores
    )
