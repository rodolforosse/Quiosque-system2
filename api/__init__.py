from flask import Blueprint, request, jsonify
from crm.models import Customers
from Pedidos import Orders, OrderItems
from Produtos.models import Products, Categories
from extensions import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/categorias', methods=['GET'])
def listar_categorias_api():
    """Retorna todas as categorias cadastradas no formato JSON"""
    categorias = Categories.query.all()
    
    lista_json = []
    for cat in categorias:
        lista_json.append({
            "id": cat.id,
            "name": cat.name  # Ajuste com o nome do campo na sua tabela
        })
        
    return jsonify(lista_json)


@api_bp.route('/api/produtos', methods=['GET'])
def listar_produtos_api():
    """Retorna todos os produtos cadastrados no formato JSON"""
    produtos = Products.query.filter_by(is_active=True).all() # Opcional: filtra apenas itens ativos
    
    lista_json = []
    for prod in produtos:
        lista_json.append({
            "id": prod.id,
            "name": prod.name,
            "preco": float(prod.price) if prod.price else 0.00,
            "description": prod.description,
            "categoria_id": prod.category_id, # Chave estrangeira ligada à categoria
            "categoria_nome": prod.category.name if prod.category else "Sem Categoria"
        })
        
    return jsonify(lista_json)


# Ajuste a rota para aceitar o método POST que o JavaScript envia
@api_bp.route('/api/pedido/criar', methods=['POST'])
def create_view():
  dados = request.get_json() or {}
  
  # Captura a propriedade enviada para decidir se é uma EDIÇÃO ou NOVO PEDIDO
  pedido_id_edicao = dados.get('pedido_id_edicao')
  
  delivery = dados.get('delivery', 'balcao')
  observation = dados.get('observation', '')
  documento = dados.get('documento_cliente', '')
  items = dados.get('items', [])
  total_value = dados.get('total_value', 0.0)

  # Resolução do Cliente Vinculado
  cliente_id = 1
  if documento:
    cliente = Customers.query.filter_by(document=documento).first()
    if cliente:
      cliente_id = cliente.id

  try:
    if pedido_id_edicao:
      # ================== MODO: ATUALIZAR PEDIDO EXISTENTE ==================
      pedido = Orders.query.get(pedido_id_edicao)
      if not pedido:
        return jsonify({"success": False, "error": "Pedido sob edição não foi localizado."}), 404
      
      # Atualiza as propriedades principais do cabeçalho existente
      pedido.customer_id = cliente_id
      pedido.delivery = delivery
      pedido.observation = observation
      pedido.total_value = total_value
      
      # Limpa fisicamente as linhas antigas de itens vinculadas a este pedido para reescrever o novo carrinho
      OrderItems.query.filter_by(order_id=pedido.id).delete()
      db.session.flush() # Aplica a limpeza na transação temporária
      
    else:
      # ================== MODO: CRIAR NOVO PEDIDO ==================
      pedido = Orders(
        customer_id=cliente_id,
        delivery=delivery,
        status='R', # Status padrão inicial
        observation=observation,
        total_value=total_value
      )
      db.session.add(pedido)
      db.session.flush()

    if not items:
      return jsonify({"success": False, "error": "O carrinho de compras está vazio."}), 400

    # Grava as novas linhas de itens com as quantidades e preços modificados no caixa
    for item in items:
      novo_item = OrderItems(
        order_id=pedido.id, # Aponta para o mesmo ID (Novo ou Existente)
        product_id=int(item['product_id']),
        quantity=int(item['quantity']),
        unit_price=float(item['unit_price'])
      )
      db.session.add(novo_item)

    # Commita a transação unificada de forma definitiva no SQLite/Postgres
    db.session.commit()
    
    return jsonify({
      "success": True, 
      "message": "Operação concluída com sucesso!", 
      "order_id": pedido.order_id
    }), 200

  except Exception as e:
    db.session.rollback()
    print(f"[ERRO NO SALVAMENTO/EDIÇÃO]: {str(e)}")
    return jsonify({"success": False, "error": f"Erro de banco de dados: {str(e)}"}), 500


# Mudamos o tipo de parâmetro para receber o ID de forma genérica e evitar quebras de rota (404/Rede)
@api_bp.route('/api/pedidos/<pedido_id>/update', methods=['POST'])
def atualizar_status_pedido(pedido_id):
  """
  Atualiza o status de um pedido de forma assíncrona.
  Suporta tanto a busca pelo ID primário quanto pelo order_id sequencial.
  """
  # Tenta localizar primeiro pelo ID primário, se falhar, busca pelo order_id sequencial
  pedido = Orders.query.filter((Orders.id == pedido_id) | (Orders.order_id == pedido_id)).first()
  
  if not pedido:
    return jsonify({"success": False, "error": "Pedido não encontrado no sistema."}), 404
    
  dados = request.get_json() or {}
  novo_status = dados.get('status')
  
  if not novo_status:
    return jsonify({"success": False, "error": "Status não informado na requisição."}), 400
      
  try:
    # Atualiza o caractere do status no banco (R, EP, PR, F, C)
    pedido.status = novo_status
    db.session.commit()
    
    return jsonify({
      "success": True, 
      "order_id": pedido.order_id,
      "status": pedido.status
    }), 200
    
  except Exception as e:
    db.session.rollback()
    return jsonify({"success": False, "error": f"Erro de banco: {str(e)}"}), 500

@api_bp.route('/api/pedido/<int:id>', methods=['GET'])
def obter_pedido_detalhes(id):
  """Retorna os dados cadastrais e as linhas do carrinho de um pedido para a API do JS"""
  pedido = Orders.query.get_or_404(id)
  
  itens_formatados = []
  for item in pedido.itens:  # Varre os OrderItems vinculados
    itens_formatados.append({
      "product_id": item.product_id,
      "product_name": item.product.name if item.product else "Item Desconhecido",
      "quantity": item.quantity,
      "unit_price": float(item.unit_price)
    })
    
  return jsonify({
    "id": pedido.id,
    "order_id": pedido.order_id,
    "delivery": pedido.delivery,
    "observation": pedido.observation or "",
    "discount": float(pedido.discount) if pedido.discount else 0.0,
    "customer_document": pedido.customer.document if pedido.customer else "",
    "itens": itens_formatados
  }), 200
