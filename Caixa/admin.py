# produtos/admin.py
from Usuarios.admin import SecureModelView
from Caixa.modelos import Caixa

class CaixaAdminView(SecureModelView):
    column_list = ['id', 'name']
    column_labels = {'id': 'ID', 'name': 'Pedidos'}

    def __init__(self, session, **kwargs):
        super(CaixaAdminView, self).__init__(Caixa, session, **kwargs)