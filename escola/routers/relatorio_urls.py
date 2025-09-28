from django.urls import path
from ..views.relatorio_view import relatorio_conteudos,relatorio_conteudos_download

app_name = 'relatorios'

urlpatterns = [
    path('conteudos/', relatorio_conteudos, name='relatorio_conteudos'),
    path('conteudos/download/', relatorio_conteudos_download, name='relatorio_conteudos_download'),
]