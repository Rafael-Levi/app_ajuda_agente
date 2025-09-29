from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from .models.professor import Professor

@receiver(post_migrate)
def criar_grupos_e_permissoes(sender, **kwargs):
    if sender.name != 'escola':
        return

    Diretoria_group, _ = Group.objects.get_or_create(name='Diretoria')
    coord_group, _ = Group.objects.get_or_create(name='Coordenação')
    prof_group, _ = Group.objects.get_or_create(name='Professor')

    codes_coord = [
        'add_agendamento','change_agendamento','delete_agendamento','view_agendamento',
        'add_aluno','change_aluno','delete_aluno','view_aluno',
    ]
    coord_perms = Permission.objects.filter(codename__in=codes_coord)
    coord_group.permissions.set(coord_perms)

    prof_perms = Permission.objects.filter(codename__in=['view_agendamento','view_aluno','change_agendamento'])
    prof_group.permissions.set(prof_perms)

    Diretoria_group.permissions.set(Permission.objects.all())

    print("Grupos (Diretoria, Coordenação, Professor) verificados/criados e permissões atribuídas.")


@receiver(post_save, sender=Professor)
def on_professor_saved(sender, instance, created, **kwargs):
    if instance.user:
        prof_group, _ = Group.objects.get_or_create(name='Professor')
        instance.user.groups.add(prof_group)


@receiver(post_save, sender=User)
def ensure_professor_for_user(sender, instance, created, **kwargs):
    if instance.groups.filter(name='Professor').exists():
        try:
            Professor.objects.get(user=instance)
        except Professor.DoesNotExist:
            Professor.objects.create(user=instance, nome=instance.get_full_name() or instance.username)
