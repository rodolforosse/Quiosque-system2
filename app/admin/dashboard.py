# produtos/admin.py
from .usuarios import SecureModelView
# from Dashboard.models import Dashboard

# class DashAdminView(SecureModelView):
#     column_list = ['id', 'name']
#     column_labels = {'id': 'ID', 'name': 'Pedidos'}
# 
#     def __init__(self, session, **kwargs):
#         super(DashAdminView, self).__init__(Dashboard, session, **kwargs)