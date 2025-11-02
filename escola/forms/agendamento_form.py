from django import forms
from ..models import agendamento, professor, aluno  as aluno_model

class AgendamentoForm(forms.ModelForm):
    SERIE_CHOICES = [
        ('', '--- Selecione ---'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]

    TURNO_CHOICES = [
        ('', '--- Selecione ---'),
        ('Manhã', 'Manhã'),
        ('Tarde', 'Tarde'),
    ]

    serie = forms.ChoiceField(choices=SERIE_CHOICES, required=False, label="Série")
    turno = forms.ChoiceField(choices=TURNO_CHOICES, required=False, label="Turno")

    class Meta:
        model = agendamento.Agendamento
        fields = ['serie', 'turno', 'aluno', 'conteudo', 'professor', 'inicio', 'duracao_minutos', 'status', 'observacoes']
        widgets = {
            'inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.groups.filter(name="Professor").exists():
            self.fields['professor'].queryset = professor.Professor.objects.filter(user=user)
        
        self.fields['aluno'].queryset = aluno_model.Aluno.objects.none()

        serie = self.data.get('serie') or self.initial.get('serie') or None
        turno = self.data.get('turno') or self.initial.get('turno') or None

        if serie and turno:
            self.fields['aluno'].queryset = aluno_model.Aluno.objects.filter(
                serie=serie,
                turno=turno
            ).order_by('nome')

        elif getattr(self.instance, "pk", None) and getattr(self.instance, "aluno", None):
            aluno_inst = self.instance.aluno
            self.fields['aluno'].queryset = aluno_model.Aluno.objects.filter(
                pk=aluno_inst.pk
            ).order_by('nome')
            self.fields['serie'].initial = aluno_inst.serie
            self.fields['turno'].initial = aluno_inst.turno
