from flask import Blueprint, render_template, request
from extensions import admin as flask_admin, db, admin_required
# from Dashboard.admin import DashAdminView
# from Dashboard.models import Dashboard

# Cria o blueprint de produtos
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

# 1. ROTA PÚBLICA: Vitrine de Produtos (ex: http://127.0.01/produtos)
@dashboard_bp.route('/dashboard')
@admin_required()
def index():
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

    # 2. Dados dos Gráficos de Linha e Barra (Fileiras 1 e 2)
    grafico_meses = ["Jan", "Fev", "Mar", "Abr", "Mai"]
    grafico_faturamento = [10500.00, 12300.50, 15430.50, 14200.00, 18900.00]
    grafico_pedidos_qtd = [80, 95, 120, 110, 140]
    
    categorias_labels = ["Eletrônicos", "Roupas", "Alimentos", "Acessórios"]
    categorias_valores = [8500.00, 4200.00, 2730.50, 1200.00]
    
    dias_labels = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    dias_valores = [45, 50, 60, 55, 80, 95, 70]
    
    horarios_labels = ["08:00", "12:00", "16:00", "20:00"]
    horarios_valores = [20, 45, 30, 65]

    # 3. Dados dos Gráficos Donut (Fileira 3) - Adicionados explicitamente aqui
    plataformas_labels = ["Painel Web", "Site", "iFood"]
    plataformas_valores = [40, 25, 35] # Certifique-se de que os valores sejam maiores que 0

    origem_labels = ["Balcão", "iFood", "WhatsApp"]
    origem_valores = [30, 50, 20]

    pagamento_labels = ["Crédito", "Débito", "Pix", "Dinheiro"]
    pagamento_valores = [35, 15, 40, 10]

    entrega_labels = ["Balcão", "Delivery"]
    entrega_valores = [30, 70]

    # 4. Envio de todas as variáveis para o Template HTML
    return render_template(
        'site/dashboard.html',
        # Configurações do Filtro
        periodos=periodos,
        periodo_selecionado=periodo_selecionado,
        
        # Cartões de Métricas Principais
        faturamento=15430.50,
        total_pedidos=120,
        ticket_medio=128.58,
        total_clientes=85,
        
        # Dados dos Gráficos de Linha e Barra
        grafico_meses=grafico_meses,
        grafico_faturamento=grafico_faturamento,
        grafico_pedidos_qtd=grafico_pedidos_qtd,
        categorias_labels=categorias_labels,
        categorias_valores=categorias_valores,
        dias_labels=dias_labels,
        dias_valores=dias_valores,
        horarios_labels=horarios_labels,
        horarios_valores=horarios_valores,
        
        # Dados Obrigatórios dos Donuts (Novas variáveis)
        plataformas_labels=plataformas_labels,
        plataformas_valores=plataformas_valores,
        origem_labels=origem_labels,
        origem_valores=origem_valores,
        pagamento_labels=pagamento_labels,
        pagamento_valores=pagamento_valores,
        entrega_labels=entrega_labels,
        entrega_valores=entrega_valores
    )


# Usamos o 'flask_admin' registrar a View
# flask_admin.add_view(DashAdminView(db.session))

