from django.urls import path,include
from .admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('agendamentos/', include('escola.routers.agendamento_urls', namespace='agendamentos')),
    path('alunos/', include('escola.routers.aluno_urls', namespace='alunos')),
    path('relatorios/', include('escola.routers.relatorio_urls', namespace='relatorios')),
    path('', include('escola.routers.login_urls', namespace='login'))
]

