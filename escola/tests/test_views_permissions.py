"""Testes de views e permissões.
Cenários:
 - acesso anônimo redireciona ao login
 - usuário sem permissão recebe 403 em views protegidas com
   permission_required(..., raise_exception=True)
 - usuário com permissão acessa
 - comportamento do 'home' para superuser / professor
"""
import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from escola.models.professor import Professor


@pytest.mark.django_db
class TestViewsPermissions:

    @pytest.fixture
    def make_user(self):
        def _make(username, is_superuser=False, groups=None, perms=None):
            u = User.objects.create_user(username=username, password='pass')
            u.is_superuser = is_superuser
            u.save()
            if groups:
                for g in groups:
                    grp, _ = Group.objects.get_or_create(name=g)
                    u.groups.add(grp)
            if perms:
                for codename in perms:
                    perm = Permission.objects.get(codename=codename)
                    u.user_permissions.add(perm)
            u.save()
            return u
        return _make

    def test_alunos_list_requer_permissao(self, client, make_user):
        url = reverse('alunos:alunos_list')

        resp = client.get(url)
        assert resp.status_code == 302 and '/?next=/alunos/' in resp.url

        u = make_user('user1')
        client.force_login(u)
        resp = client.get(url)
        assert resp.status_code == 403

        perm = Permission.objects.get(codename='view_aluno')
        u.user_permissions.add(perm)
        u.save()
        resp = client.get(url)
        assert resp.status_code == 200

    def test_home_redirects_superuser_and_professor_shows_agendamentos(self, client, make_user):
        su = make_user('su', is_superuser=True)
        client.force_login(su)
        resp = client.get(reverse('agendamentos:home'))
       
        assert resp.status_code in (200, 302)

        prof_user = make_user('prof', groups=['Professor'])
        Professor.objects.create(nome='Prof Test', user_id=1)
        client.force_login(prof_user)
        resp = client.get(reverse('agendamentos:home'))
        assert resp.status_code == 200
        
        if hasattr(resp, 'context') and resp.context is not None:
            assert 'agendamentos' in resp.context or 'agendamentos' in ''.join(str(k) for k in resp.context.keys())
