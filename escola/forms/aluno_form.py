from django import forms
from ..models import aluno

class AlunoForm(forms.ModelForm):
    class Meta:
        model = aluno.Aluno
        fields = ['nome','telefone','serie','turno']
