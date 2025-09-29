from django.db import models

class Conteudo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    duracao_minutos = models.PositiveIntegerField(default=60)  # duração padrão
    descritor = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return self.nome