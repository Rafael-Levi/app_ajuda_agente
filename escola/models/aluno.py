from django.db import models

class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    serie = models.CharField(max_length=10, blank=True, null=False)
    turma = models.CharField(max_length=10, blank=True, null=False)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nome
