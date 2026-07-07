"""
Seed script para criar um Caixa aberto com movimentações de exemplo.
Rode com o virtualenv ativado na raiz do projeto:

  python scripts/seed_caixa.py

Atenção: este script tenta usar a fábrica create_app() do projeto. Se seu projeto inicializa a app de forma diferente,
ajuste o import (ex: from run import app) ou crie um usuário previamente no /admin.
"""
from datetime import datetime
from decimal import Decimal

try:
    # tentativa padrão: app com factory create_app
    from app import create_app
    from app.extensions import db
    from app.models import User, Caixadb, MovimentacaoCaixa
    app = create_app()
except Exception:
    # fallback: tenta importar diretório raiz (ajuste conforme seu projeto)
    try:
        from run import app  # se você tem run.py que cria a app
        from app.extensions import db
        from app.models import User, Caixadb, MovimentacaoCaixa
    except Exception as e:
        print("Não foi possível importar a aplicação automaticamente:", e)
        print("Ajuste este script para usar a forma correta de criar/obter a app (create_app ou run.app).")
        raise

with app.app_context():
    # busca um usuário existente para associar como user_abertura/user_id nas movimentações
    user = None
    try:
        user = User.query.first()
    except Exception:
        user = None

    if not user:
        print("Nenhum usuário encontrado no banco. Crie um usuário via /admin ou ajuste este script para criar um usuário temporário.")
        # não tentaremos criar um usuário automático para evitar regras de validação do modelo

    # cria caixa aberto
    caixa = Caixadb(
        status='aberto',
        valor_inicial=Decimal('45.60'),
        user_abertura_id=(user.id if user else 1),
        data_abertura=datetime.utcnow()
    )
    db.session.add(caixa)
    db.session.flush()

    # cria movimentações de exemplo (simulando pedidos vendidos)
    m1 = MovimentacaoCaixa(
        caixa_id=caixa.id,
        order_id=None,
        tipo='venda',
        valor=Decimal('17.90'),
        metodo_pagamento='cartao_debito',
        data_movimento=datetime.utcnow(),
        user_id=(user.id if user else 1),
        descricao='Pedido #1124047 Balcão'
    )

    m2 = MovimentacaoCaixa(
        caixa_id=caixa.id,
        order_id=None,
        tipo='venda',
        valor=Decimal('12.90'),
        metodo_pagamento='cartao_debito',
        data_movimento=datetime.utcnow(),
        user_id=(user.id if user else 1),
        descricao='Pedido #1124050 Balcão'
    )

    db.session.add_all([m1, m2])
    db.session.commit()

    print(f"Seed concluído: Caixa id={caixa.id} criado com 2 movimentações de exemplo.")
