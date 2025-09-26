from django.contrib import admin
from escola.models import aluno, conteudo, professor, agendamento
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin

class CustomAdminSite(admin.AdminSite):
    site_header = "Agendamento reforço - backoffice"

admin_site = CustomAdminSite()

admin_site.register(professor.Professor)
admin_site.register(agendamento.Agendamento)
admin_site.register(aluno.Aluno)
admin_site.register(conteudo.Conteudo)

admin_site.register(User, UserAdmin)
admin_site.register(Group)