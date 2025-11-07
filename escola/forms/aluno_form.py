from django import forms
from ..models.aluno import Aluno

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome','telefone','serie','turno','is_active']
        labels={
            Aluno.is_active:'Aluno ativo'
        }
