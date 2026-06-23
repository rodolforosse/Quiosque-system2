# produtos/admin.py
from Usuarios.admin import SecureModelView
from Pedidos.modelos import Orders

class OrdersAdminView(SecureModelView):
    column_list = ['id', 'name']
    column_labels = {'id': 'ID', 'name': 'Pedidos'}

    def __init__(self, session, **kwargs):
        super(OrdersAdminView, self).__init__(Orders, session, **kwargs)