from django.http import JsonResponse
from ..models.aluno import Aluno

def load_alunos(request):
    serie = request.GET.get('serie')
    turno = request.GET.get('turno')

    alunos = Aluno.objects.filter(
        serie=serie,
        turno=turno
    ).order_by('nome')

    return JsonResponse(list(alunos.values('id', 'nome')), safe=False)
