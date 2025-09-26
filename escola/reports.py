from django.db.models import Count

def concluido_por_conteudo(queryset, start_dt, end_dt):
    """
    Retorna uma lista com {'conteudo': nome, 'total': n} para agendamentos CONCLUIDOS
    dentro do período [start_dt, end_dt).
    queryset: Agendamento.objects.all() ou filtrado
    """
    qs = queryset.filter(
        status='CONCLUIDO',
        inicio__gte=start_dt,
        inicio__lt=end_dt
    ).values('conteudo__nome').annotate(total=Count('id')).order_by('-total')
    return list(qs)
