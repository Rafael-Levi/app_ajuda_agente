from django.urls import path
from ..views.aluno_view import aluno_create,aluno_edit,alunos_list

app_name = 'alunos'

urlpatterns = [
    path('', alunos_list, name='alunos_list'),
    path('novo/', aluno_create, name='aluno_create'),
    path('<int:pk>/editar/', aluno_edit, name='aluno_edit'),
]