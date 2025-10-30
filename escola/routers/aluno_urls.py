from django.urls import path
from ..views.aluno_view import aluno_create,aluno_edit,alunos_list
from ..views.ajax import load_alunos

app_name = 'alunos'

urlpatterns = [
    path("ajax/load-alunos/", load_alunos, name="ajax_load_alunos"),
    path('', alunos_list, name='alunos_list'),
    path('novo/', aluno_create, name='aluno_create'),
    path('editar/<int:pk>/', aluno_edit, name='aluno_edit'),
]