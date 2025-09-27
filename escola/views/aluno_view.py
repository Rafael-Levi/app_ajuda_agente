from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from ..models.agendamento import Aluno
from ..forms.aluno_form import AlunoForm

@login_required
@permission_required('escola.add_aluno', raise_exception=True)
def aluno_create(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('alunos:alunos_list')
    else:
        form = AlunoForm()
    return render(request, 'alunos/aluno_form.html', {'form': form, 'title': 'Adicionar aluno'})

@login_required
@permission_required('escola.change_aluno', raise_exception=True)
def aluno_edit(request, pk):
    aluno = get_object_or_404(aluno, pk=pk)
    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            return redirect('alunos_list')
    else:
        form = AlunoForm(instance=aluno)
    return render(request, 'alunos/aluno_form.html', {'form': form, 'title': 'Editar aluno'})

@login_required
@permission_required('escola.view_aluno', raise_exception=True)
def alunos_list(request):
    alunos = Aluno.objects.all()
    return render(request, 'alunos/alunos_list.html', {'alunos': alunos})
