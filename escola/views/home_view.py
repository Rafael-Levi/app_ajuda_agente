from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from ..models.agendamento import Agendamento, Professor
from ..forms.agendamento_form import AgendamentoForm
from django.http import HttpResponseBadRequest

@login_required
def home(request):
    user = request.user

    if user.is_superuser or user.groups.filter(name="Diretoria").exists():
        return redirect('/admin/')

    if user.groups.filter(name="Coordenação").exists():
        agendamentos = Agendamento.objects.select_related('aluno', 'conteudo', 'professor').all()
        return render(request, 'home/home_coordenacao.html', {'agendamentos': agendamentos})

    if user.groups.filter(name="Professor").exists():
        prof = None
        try:
            prof = Professor.objects.get(user=user)
        except Professor.DoesNotExist:
            try:
                nome = user.get_full_name() or user.username
                prof = Professor.objects.get(nome__iexact=nome)
            except Professor.DoesNotExist:
                prof = None

        if prof:
            agendamentos = Agendamento.objects.select_related('aluno', 'conteudo').filter(professor=prof)
        else:
            agendamentos = Agendamento.objects.none()
        return render(request, 'home/home_professor.html', {'agendamentos': agendamentos, 'professor': prof})

    return render(request, 'home/home_default.html')


class AgendamentoListView(LoginRequiredMixin, ListView):
    model = Agendamento
    paginate_by = 20
    template_name = 'agendamentos/agendamento_list.html'
    context_object_name = 'agendamentos'

    def get_queryset(self):
        qs = super().get_queryset().select_related('aluno', 'conteudo', 'professor')
        user = self.request.user

        if user.is_superuser or user.groups.filter(name='Coordenação').exists():
            return qs
        if user.groups.filter(name='professor').exists():
            try:
                prof = Professor.objects.get(user=user)
            except Professor.DoesNotExist:
                try:
                    prof = Professor.objects.get(nome__iexact=user.get_full_name() or user.username)
                except Professor.DoesNotExist:
                    return Agendamento.objects.none()
            return qs.filter(Professor=prof)
        return Agendamento.objects.none()


class AgendamentoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'escola.add_agendamento'
    model = Agendamento
    form_class = AgendamentoForm
    template_name = 'agendamentos/agendamento_form.html'
    success_url = reverse_lazy('agendamentos:list')

    def get_form(self, form_class=None):
        """
        Garante que o form receba request.GET para pré-filtrar alunos
        caso AJAX ou redirecionamento preserve filtros na URL.
        """
        form = super().get_form(form_class)
        form.data = self.request.POST or self.request.GET
        return form



class AgendamentoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'escola.change_agendamento'
    model = Agendamento
    form_class = AgendamentoForm
    template_name = 'agendamentos/agendamento_form.html'
    success_url = reverse_lazy('agendamentos:list')


class AgendamentoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'escola.delete_agendamento'
    model = Agendamento
    template_name = 'agendamentos/agendamento_confirm_delete.html'
    success_url = reverse_lazy('agendamentos:list')


class AgendamentoDetailView(LoginRequiredMixin, DetailView):
    model = Agendamento
    template_name = 'agendamentos/agendamento_detail.html'


@login_required
def alterar_status_agendamento(request, pk):
    """
    Altera o status de um agendamento.
    - Somente POST é aceito.
    - Professor só pode alterar seus próprios agendamentos.
    - Coordenação e Admin podem alterar qualquer agendamento.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Apenas POST permitido.")

    novo_status = request.POST.get('status')
    allowed_status = [s[0] for s in Agendamento.STATUS_CHOICES]
    if novo_status not in allowed_status:
        return HttpResponseBadRequest("Status inválido.")

    agendamento = get_object_or_404(Agendamento, pk=pk)
    user = request.user

    if user.groups.filter(name='professor').exists():
        try:
            prof = Professor.objects.get(user=user)
        except Professor.DoesNotExist:
            return redirect('agendamentos:home')
        if agendamento.professor != prof:
            return redirect('agendamentos:home')

    agendamento.status = novo_status
    agendamento.save()
    return redirect('agendamentos:home')
