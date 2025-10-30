from django import forms
from ..models import agendamento, aluno as aluno_model

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
        super().__init__(*args, **kwargs)

        # default: vazio para evitar mostrar todos os alunos
        self.fields['aluno'].queryset = aluno_model.Aluno.objects.none()

        # 1) Se veio via POST/GET (interação), tente filtrar pelo que foi enviado
        # Note: self.data funciona tanto para POST quanto GET dependendo de como o form é construído na view
        serie = self.data.get('serie') or self.initial.get('serie') or None
        turno = self.data.get('turno') or self.initial.get('turno') or None

        if serie and turno:
            self.fields['aluno'].queryset = aluno_model.Aluno.objects.filter(
                serie=serie,
                turno=turno
            ).order_by('nome')

        # 2) Se for edição (instance) e aluno já existe, permita mostrar o aluno atual
        elif getattr(self.instance, "pk", None) and getattr(self.instance, "aluno", None):
            aluno_inst = self.instance.aluno
            self.fields['aluno'].queryset = aluno_model.Aluno.objects.filter(
                pk=aluno_inst.pk
            ).order_by('nome')
            # pré-preenche os campos serie/turno para edição
            self.fields['serie'].initial = aluno_inst.serie
            self.fields['turno'].initial = aluno_inst.turno
