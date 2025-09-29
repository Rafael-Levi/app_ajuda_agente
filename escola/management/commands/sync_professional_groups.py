from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from escola.models.agendamento import Professor

class Command(BaseCommand):
    help = 'Sincroniza grupos Professor e cria objetos Professor para usuários no grupo Professor (se necessário)'

    def handle(self, *args, **options):
        prof_group, _ = Group.objects.get_or_create(name='Professor')
        #usuários ligados a Professor.user -> garante grupo
        count_linked = 0
        for prof in Professor.objects.filter(user__isnull=False):
            prof.user.groups.add(prof_group)
            count_linked += 1

        #usuários no grupo Professor -> cria Professor se não existir
        count_created = 0
        users = User.objects.filter(groups__name='Professor')
        for u in users:
            try:
                _ = Professor.objects.get(user=u)
            except Professor.DoesNotExist:
                Professor.objects.create(user=u, nome=u.get_full_name() or u.username)
                count_created += 1

        self.stdout.write(self.style.SUCCESS(f'Users linked to Professor group: {count_linked}'))
        self.stdout.write(self.style.SUCCESS(f'Professor objects created for users in group: {count_created}'))
