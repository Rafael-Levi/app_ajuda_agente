"""Testes de conflito de horário para Agendamento.
Cenários cobertos:
 - criação de agendamento sem conflito
 - tentativa de criar agendamento que conflita -> ValidationError
 - agendamento que começa exatamente quando o outro termina (sem conflito)
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from escola.models import aluno, conteudo, professor, agendamento


@pytest.mark.django_db
class TestAgendamentoConflict:

    @pytest.fixture
    def base_objs(self):
        a = aluno.Aluno.objects.create(nome='Aluno Teste')
        c = conteudo.Conteudo.objects.create(nome='Conteudo Teste', duracao_minutos=60, descricao='desc', descritor='d')
        p = professor.Professor.objects.create(nome='Professor Teste')
        return a, c, p

    def test_criar_sem_conflito(self, base_objs):
        a, c, p = base_objs
        inicio = timezone.now() + timedelta(days=1, hours=2)
        ag1 = agendamento.Agendamento.objects.create(aluno=a, conteudo=c, professor=p, inicio=inicio)
        inicio2 = inicio + timedelta(minutes=c.duracao_minutos)
        ag2 = agendamento.Agendamento.objects.create(aluno=a, conteudo=c, professor=p, inicio=inicio2)
        assert ag1.pk is not None
        assert ag2.pk is not None

    def test_criar_com_conflito_levanta_validation_error(self, base_objs):
        a, c, p = base_objs
        inicio = timezone.now() + timedelta(days=1, hours=2)
        ag1 = agendamento.Agendamento.objects.create(aluno=a, conteudo=c, professor=p, inicio=inicio)
        inicio_overlap = inicio + timedelta(minutes=30)
        ag2 = agendamento.Agendamento(aluno=a, conteudo=c, professor=p, inicio=inicio_overlap)
        with pytest.raises(ValidationError):
            ag2.full_clean()

    def test_toque_exato_no_fim_eh_permitido(self, base_objs):
        a, c, p = base_objs
        inicio = timezone.now() + timedelta(days=1, hours=2)
        ag1 = agendamento.Agendamento.objects.create(aluno=a, conteudo=c, professor=p, inicio=inicio)
        fim_ag1 = ag1.inicio + timedelta(minutes=(ag1.duracao_minutos or c.duracao_minutos))
        ag2 = agendamento.Agendamento.objects.create(aluno=a, conteudo=c, professor=p, inicio=fim_ag1)
        assert ag2.pk is not None
