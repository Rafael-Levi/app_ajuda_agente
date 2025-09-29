"""Testes simples de CRUD para Conteudo (model-level).
"""
import pytest
from escola.models import conteudo


@pytest.mark.django_db
def test_conteudo_crud_model():
    c = conteudo.Conteudo.objects.create(nome='C1', descricao='d', duracao_minutos=45, descritor='desc')
    assert conteudo.Conteudo.objects.filter(pk=c.pk).exists()

    c2 = conteudo.Conteudo.objects.get(pk=c.pk)
    assert c2.nome == 'C1'

    c2.nome = 'C1 alt'
    c2.save()
    assert conteudo.Conteudo.objects.get(pk=c.pk).nome == 'C1 alt'

    c2.delete()
    assert conteudo.Conteudo.objects.filter(pk=c.pk).count() == 0