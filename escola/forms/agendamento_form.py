from django import forms
from ..models import agendamento, aluno

class AgendamentoForm(forms.ModelForm):
    SERIE_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]

    TURNO_CHOICES = [
        ('M', 'Manhã'),
        ('T', 'Tarde'),
    ]

    # Campos extras para o filtro
    serie = forms.ChoiceField(choices=SERIE_CHOICES, required=True, label="Série")
    turno = forms.ChoiceField(choices=TURNO_CHOICES, required=True, label="Turno")

    class Meta:
        model = agendamento.Agendamento
        fields = ['serie', 'turno', 'aluno', 'conteudo', 'professor', 'inicio', 'duracao_minutos', 'status', 'observacoes']
        widgets = {
            'inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Inicialmente: nenhum aluno
        self.fields['aluno'].queryset = aluno.Aluno.objects.none()

        # Se o formulário foi interagido, filtrar os alunos
        if 'serie' in self.data and 'turno' in self.data:
            serie = self.data.get('serie')
            turno = self.data.get('turno')
            if serie and turno:
                self.fields['aluno'].queryset = aluno.Aluno.objects.filter(
                    serie=serie,
                    turno=turno
                ).order_by('nome')

        # Se for edição de agendamento existente, mostrar aluno já salvo
        elif self.instance.pk:
            self.fields['aluno'].queryset = aluno.Aluno.objects.filter(
                serie=self.instance.aluno.serie,
                turno=self.instance.aluno.turno
            ).order_by('nome')
            self.fields['serie'].initial = self.instance.aluno.serie
            self.fields['turno'].initial = self.instance.aluno.turno
