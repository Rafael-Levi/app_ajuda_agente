from django.contrib import admin
from .models import agendamento, aluno, conteudo, professor

@admin.register(aluno.Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'serie', 'turno','telefone')
    search_fields = ('nome', 'serie', 'turno',"telefone")


@admin.register(conteudo.Conteudo)
class ConteudoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'duracao_minutos', 'descricao','descritor')
    search_fields = ('nome','duracao_minutos', 'descricao','descritor')


@admin.register(professor.Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'user', 'especialidade')
    search_fields = ('nome', 'especialidade', 'user__username')


@admin.register(agendamento.Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'aluno', 'conteudo', 'professor', 'inicio', 'status')
    list_filter = ('status', 'professor', 'conteudo')
    search_fields = ('aluno__nome', 'professor__nome', 'conteudo__nome')
    ordering = ('-inicio',)
    date_hierarchy = 'inicio'
