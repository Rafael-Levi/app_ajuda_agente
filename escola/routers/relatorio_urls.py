from django.urls import path
from ..views import relatorio_view
app_name = "relatorios"

urlpatterns = [
    path("conteudos/", relatorio_view.relatorio_conteudos, name="relatorio_conteudos"),
    path("conteudos/json/", relatorio_view.relatorio_conteudos_json, name="relatorio_conteudos_json"),
    path("conteudos/export/", relatorio_view.export_relatorio_excel, name="export_relatorio_excel"),
]