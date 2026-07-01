from .usuarios import SecureModelView
from app.models import Caixadb, MovimentacaoCaixa

    

class CaixaAdminView(SecureModelView):
    column_list = ['id', 'name']
    column_labels = {'id': 'ID', 'name': 'Categoria'}

    def __init__(self, session, **kwargs):
        super(CaixaAdminView, self).__init__(Caixadb, session, **kwargs)


class MovimentacaoCaixaAdminView(SecureModelView):
    column_list = ['id', 'name']
    column_labels = {'id': 'ID', 'name': 'Categoria'}

    def __init__(self, session, **kwargs):
        super(MovimentacaoCaixaAdminView, self).__init__(
            MovimentacaoCaixa, session, **kwargs)
    