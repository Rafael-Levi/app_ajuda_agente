from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models.agendamento import Agendamento
from ..forms.relatorio_form import RelatorioForm
from ..reports import concluido_por_conteudo
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest,HttpResponse
import io
import pandas as pd
from django.db.models import F

def relatorio_conteudos(request):
    form = RelatorioForm(request.GET or None)
    data = []
    if form.is_valid():
        start = form.cleaned_data['start']
        end = form.cleaned_data['end']
        start_dt = datetime.combine(start, datetime.min.time())
        end_dt = datetime.combine(end, datetime.max.time())
        data = concluido_por_conteudo(Agendamento.objects.all(), start_dt, end_dt)
    else:
        end_dt = timezone.now()
        start_dt = end_dt - timedelta(days=30)
        data = concluido_por_conteudo(Agendamento.objects.all(), start_dt, end_dt)
        form = RelatorioForm(initial={'start': start_dt.date(), 'end': end_dt.date()})

    return render(request, 'relatorio/relatorio_conteudos.html', {'form': form, 'data': data})


@login_required
def relatorio_conteudos_download(request):

    start = request.GET.get('start')
    end = request.GET.get('end')
    if not start or not end:
        return HttpResponseBadRequest("Parâmetros 'start' e 'end' são obrigatórios no formato YYYY-MM-DD.")

    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
    except Exception:
        return HttpResponseBadRequest("Formato de data inválido. Use YYYY-MM-DD.")

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    # Query otimizada — traz apenas campos necessários
    qs = Agendamento.objects.select_related('conteudo', 'professor', 'aluno').filter(
        inicio__gte=start_dt, inicio__lte=end_dt
    )

    rows = qs.values(
        'id',
        'inicio',
        'duracao_minutos',
        'status',
        conteudo_nome=F('conteudo__nome'),
        conteudo_duracao=F('conteudo__duracao_minutos'),
        conteudo_preco=F('conteudo__preco'),
        professor_nome=F('professor__nome'),
        aluno_nome=F('aluno__nome'),
    )

    df = pd.DataFrame(list(rows))

    # Se não há dados, retornar um excel simples com aviso
    if df.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame([{'message': 'Nenhum dado no período selecionado.'}]).to_excel(writer, index=False, sheet_name='Resumo')
        output.seek(0)
        filename = f"relatorio_conteudos_{start}_{end}.xlsx"
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    for col in df.select_dtypes(include=['datetimetz']).columns:
        df[col] = pd.to_datetime(df[col]).dt.tz_localize(None)


    df['duracao_calc'] = df.apply(
        lambda r: r['duracao_minutos'] if r['duracao_minutos'] not in (None, 0) else r.get('conteudo_duracao', None),
        axis=1
    )

    # insights
    total_concluidos = int((df['status'] == 'CONCLUIDO').sum())
    total_cancelados = int((df['status'] == 'CANCELADO').sum())
    total_agendados = int((df['status'] == 'AGENDADO').sum())

    concluidos = df[df['status'] == 'CONCLUIDO']
    total_por_prof = (concluidos.groupby('professor_nome')
                      .size().reset_index(name='total_concluidos')
                      .sort_values('total_concluidos', ascending=False))

    top_conteudos = (concluidos.groupby('conteudo_nome')
                    .size().reset_index(name='total')
                    .sort_values('total', ascending=False))

    media_dur_serv = (df.groupby('conteudo_nome')['duracao_calc']
                      .mean().reset_index(name='duracao_media_minutos'))

    df['dia'] = pd.to_datetime(df['inicio']).dt.date
    por_dia = df.groupby('dia').size().reset_index(name='total')

    # Monta Excel em memória
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        df[['id','inicio','professor_nome','aluno_nome','conteudo_nome','status','duracao_calc']].to_excel(writer, index=False, sheet_name='RawData')

        resumo = pd.DataFrame([
            {'metric':'total_concluidos','value': total_concluidos},
            {'metric':'total_cancelados','value': total_cancelados},
            {'metric':'total_agendados','value': total_agendados},
            {'metric':'period_start','value': start},
            {'metric':'period_end','value': end},
        ])
        resumo.to_excel(writer, index=False, sheet_name='Resumo')

        total_por_prof.to_excel(writer, index=False, sheet_name='Concluidos_por_Professor')
        top_conteudos.to_excel(writer, index=False, sheet_name='Top_conteudos')
        media_dur_serv.to_excel(writer, index=False, sheet_name='Media_Duracao_Por_conteudo')
        por_dia.to_excel(writer, index=False, sheet_name='Agendamentos_por_Dia')

    output.seek(0)
    filename = f"relatorio_conteudos_{start}_{end}.xlsx"
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
