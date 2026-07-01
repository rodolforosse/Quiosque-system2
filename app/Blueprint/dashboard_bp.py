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
        'order': 5,
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
    
    return (hoje.replace(hour=0, minute=0, second=0), hoje.replace(hour=23, minute=59, second=59))


@dashboard_bp.route('/dashboard')
@admin_required()
def index():
    periodos = {
        'hoje': 'Hoje',
        'ontem': 'Ontem',
        'estemes': 'Este mês',
        'mespassado': 'Mês passado',
        'esteano': 'Este ano',
        'anopassado': 'Ano passado',
        'personalizado': 'Personalizado'
    }
    
    periodo_selecionado = request.args.get('periodo', 'hoje')
    data_inicio, data_fim = get_date_range(periodo_selecionado)
    
    # 2. CÁLCULO DE MÉTRICAS PRINCIPAIS
    total_faturamento = db.session.query(func.sum(Orders.total_value)).filter(
        Orders.created_at >= data_inicio,
        Orders.created_at <= data_fim,
        Orders.status != 'C'
    ).scalar() or 0
    
    total_pedidos = db.session.query(func.count(Orders.id)).filter(
        Orders.created_at >= data_inicio,
        Orders.created_at <= data_fim,
        Orders.status != 'C'
    ).scalar() or 0
    
    ticket_medio = float(total_faturamento) / total_pedidos if total_pedidos > 0 else 0
    
    total_clientes = db.session.query(func.count(Customers.id)).filter(
        Customers.ativo == True
    ).scalar() or 0
    
    # 3. DADOS DOS GRÁFICOS DE MESES
    grafico_meses = []
    grafico_faturamento = []
    grafico_pedidos_qtd = []
    
    hoje = datetime.now()
    for i in range(4, -1, -1):
        ano_alvo = hoje.year
        mes_alvo = hoje.month - i
        while mes_alvo <= 0:
            mes_alvo += 12
            ano_alvo -= 1
            
        mes_inicio = datetime(ano_alvo, mes_alvo, 1, 0, 0, 0)
        
        if mes_alvo == 12:
            mes_fim = datetime(ano_alvo + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            mes_fim = datetime(ano_alvo, mes_alvo + 1, 1, 0, 0, 0) - timedelta(seconds=1)
        
        faturamento_mes = db.session.query(func.sum(Orders.total_value)).filter(
            Orders.created_at >= mes_inicio, Orders.created_at <= mes_fim, Orders.status != 'C'
        ).scalar() or 0
        
        pedidos_mes = db.session.query(func.count(Orders.id)).filter(
            Orders.created_at >= mes_inicio, Orders.created_at <= mes_fim, Orders.status != 'C'
        ).scalar() or 0
        
        grafico_meses.append(mes_inicio.strftime("%b"))
        grafico_faturamento.append(float(faturamento_mes))
        grafico_pedidos_qtd.append(pedidos_mes)

    # 3.1 DADOS DOS DIAS
    dias_labels = []
    dias_valores = []
    for i in range(6, -1, -1):
        dia_alvo = hoje - timedelta(days=i)
        inicio_dia = dia_alvo.replace(hour=0, minute=0, second=0)
        fim_dia = dia_alvo.replace(hour=23, minute=59, second=59)
        
        faturamento_dia = db.session.query(func.sum(Orders.total_value)).filter(
            Orders.created_at >= inicio_dia,
            Orders.created_at <= fim_dia,
            Orders.status != 'C'
        ).scalar() or 0
        
        dias_labels.append(dia_alvo.strftime("%d/%m"))
        dias_valores.append(float(faturamento_dia))

    # 3.2 DADOS DE HORÁRIOS (Correção sem quebra do strftime em bancos diferentes)
    horarios_labels = [f"{h:02d}:00" for h in range(24)]
    horarios_valores = [0.0] * 24
    
    pedidos_hoje = db.session.query(Orders.created_at, Orders.total_value).filter(
        Orders.created_at >= hoje.replace(hour=0, minute=0, second=0),
        Orders.created_at <= hoje.replace(hour=23, minute=59, second=59),
        Orders.status != 'C'
    ).all()
    
    for pedido in pedidos_hoje:
        if pedido.created_at:
            hora = pedido.created_at.hour
            if 0 <= hora < 24:
                horarios_valores[hora] += float(pedido.total_value or 0)
    
    # 4. OTIMIZAÇÃO DE QUERIES
    pedidos_por_plataforma = dict(db.session.query(Orders.delivery, func.count(Orders.id)).group_by(Orders.delivery).all())
    plataformas_labels = ["Balcão", "iFood", "WhatsApp"]
    plataformas_valores = [
        pedidos_por_plataforma.get('balcao', 0),
        pedidos_por_plataforma.get('ifood', 0),
        pedidos_por_plataforma.get('whatsapp', 0)
    ]
    
    pedidos_por_status = dict(db.session.query(Orders.status, func.count(Orders.id)).group_by(Orders.status).all())
    origem_labels = ["Realizado", "Em Prep.", "Pronto", "Finalizado"]
    origem_valores = [
        pedidos_por_status.get('R', 0),
        pedidos_por_status.get('EP', 0),
        pedidos_por_status.get('PR', 0),
        pedidos_por_status.get('F', 0)
    ]
    
    entrega_labels = ["Balcão", "Delivery"]
    entrega_valores = [
        pedidos_por_plataforma.get('balcao', 0),
        sum(pedidos_por_plataforma.get(k, 0) for k in ['ifood', 'whatsapp', 'delivery'] if k in pedidos_por_plataforma)
    ]
    
    # LINHA CORRIGIDA DEFINITIVAMENTE:
    pagamento_labels = ["Dinheiro", "PIX", "Crédito", "Débito"]
    pagamento_valores = [25, 45, 20, 10]
    
    categorias_labels = ["Eletrônicos", "Roupas", "Alimentos", "Acessórios"]
    categorias_valores = [8500.00, 4200.00, 2730.50, 1200.00]
    
    return render_template(
        'site/dashboard.html',
        periodos=periodos,
        periodo_selecionado=periodo_selecionado,
        faturamento=float(total_faturamento),
        total_pedidos=total_pedidos,
        ticket_medio=round(ticket_medio, 2),
        total_clientes=total_clientes,
        
        # Injeção de variáveis de dias e horas
        dias_labels=dias_labels,
        dias_valores=dias_valores,
        horarios_labels=horarios_labels,
        horarios_valores=horarios_valores,
        
        grafico_meses=grafico_meses,
        grafico_faturamento=grafico_faturamento,
        grafico_pedidos_qtd=grafico_pedidos_qtd,
        categorias_labels=categorias_labels,
        categorias_valores=categorias_valores,
        plataformas_labels=plataformas_labels,
        plataformas_valores=plataformas_valores,
        origem_labels=origem_labels,
        origem_valores=origem_valores,
        pagamento_labels=pagamento_labels,
        pagamento_valores=pagamento_valores,
        entrega_labels=entrega_labels,
        entrega_valores=entrega_valores
    )
