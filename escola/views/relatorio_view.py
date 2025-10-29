# app_ajuda_agente/escola/views/relatorio_view.py
import io
from datetime import datetime, time
import pandas as pd

from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from escola.forms.relatorio_form import RelatorioForm
from escola.models.agendamento import Agendamento

# =============== AUXILIAR DE PARSE DE DATAS ===============
def _parse_date(date_str):
    """
    Converte string de data (YYYY-MM-DD) ou ISO datetime em datetime.date.
    Retorna None se não for possível parsear.
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.fromisoformat(date_str).date()
        except Exception:
            return None


# =========================================================
# =============== GERADOR DE DADOS DO RELATÓRIO ============
# =========================================================
def _generate_report_data(start_date, end_date):
    """
    Gera os dados (em estruturas simples: dicts/listas) usados no template e no XLSX.
    start_date, end_date: datetime.date (se None, default é últimos 30 dias)
    Retorna dict com chaves:
      resumo, by_professor, by_aluno, by_conteudo, monthly, agendamentos_rows
    """
    # Normaliza datas com fallback de 30 dias
    if not start_date and not end_date:
        end_dt = timezone.localdate()
        start_dt = end_dt - pd.Timedelta(days=30)
    else:
        end_dt = end_date or timezone.localdate()
        start_dt = start_date or (end_dt - pd.Timedelta(days=30))

    # Converte para datetimes (início do dia / fim do dia)
    start_dt_dt = datetime.combine(start_dt, time.min)
    end_dt_dt = datetime.combine(end_dt, time.max)

    # Tenta tornar timezone-aware se for possível (mantendo compatibilidade)
    try:
        start_dt_dt = timezone.make_aware(start_dt_dt)
        end_dt_dt = timezone.make_aware(end_dt_dt)
    except Exception:
        # Se já estiver aware ou não for possível, segue com os valores originais
        pass

    qs = (
        Agendamento.objects.select_related("aluno", "conteudo", "professor")
        .filter(inicio__gte=start_dt_dt, inicio__lte=end_dt_dt)
        .order_by("inicio")
    )

    rows = []
    for ag in qs:
        aluno = getattr(ag, "aluno", None)
        conteudo = getattr(ag, "conteudo", None)
        prof = getattr(ag, "professor", None)
        rows.append(
            {
                "id": ag.id,
                "inicio": ag.inicio,
                "duracao_minutos": ag.duracao_minutos or 0,
                "status": ag.status,
                "aluno": aluno.nome if aluno else "",
                "serie": aluno.serie if aluno else "",
                "turma": aluno.turma if aluno else "",
                "professor": prof.nome if prof else "",
                "especialidade": prof.especialidade if prof else "",
                "conteudo": conteudo.nome if conteudo else "",
                "descritor": conteudo.descritor if conteudo else "",
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        # Garante as colunas para evitar KeyError em operações seguintes
        df = pd.DataFrame(
            columns=[
                "id",
                "inicio",
                "duracao_minutos",
                "status",
                "aluno",
                "serie",
                "turma",
                "professor",
                "especialidade",
                "conteudo",
                "descritor",
            ]
        )

    # --- Cálculos e transformações ---
    df["duracao_horas"] = df["duracao_minutos"].fillna(0) / 60
    df["inicio"] = pd.to_datetime(df["inicio"], errors="coerce").dt.tz_localize(None)
    df["mes"] = df["inicio"].dt.to_period("M").astype(str)

    total_agendamentos = len(df)
    total_horas = df["duracao_horas"].sum()
    media_duracao = df["duracao_minutos"].mean() if total_agendamentos else 0

    # Agrupamentos (DataFrames)
    by_professor = (
        df.groupby("professor")
        .agg(agendamentos=("id", "count"), horas=("duracao_horas", "sum"))
        .reset_index()
        .sort_values("agendamentos", ascending=False)
    )

    by_aluno = (
        df.groupby("aluno")
        .agg(agendamentos=("id", "count"), horas=("duracao_horas", "sum"))
        .reset_index()
        .sort_values("agendamentos", ascending=False)
    )

    by_conteudo = (
        df.groupby("conteudo")
        .agg(agendamentos=("id", "count"), horas=("duracao_horas", "sum"))
        .reset_index()
        .sort_values("agendamentos", ascending=False)
    )

    monthly = (
        df.groupby("mes")
        .agg(agendamentos=("id", "count"), horas=("duracao_horas", "sum"))
        .reset_index()
        .sort_values("mes")
    )

    resumo = {
        "periodo_inicial": start_dt,
        "periodo_final": end_dt,
        "total_agendamentos": int(total_agendamentos),
        "total_horas": round(float(total_horas), 2),
        "media_duracao_min": round(float(media_duracao or 0), 1),
    }

    # Converte para listas de dicts (fácil render no template / JSON)
    def df_to_list(df_obj, cols=None):
        if df_obj is None:
            return []
        if cols:
            df_obj = df_obj[cols]
        return df_obj.fillna("").to_dict(orient="records")

    return {
        "resumo": resumo,
        "by_professor": df_to_list(by_professor, cols=["professor", "agendamentos", "horas"]),
        "by_aluno": df_to_list(by_aluno, cols=["aluno", "agendamentos", "horas"]),
        "by_conteudo": df_to_list(by_conteudo, cols=["conteudo", "agendamentos", "horas"]),
        "monthly": df_to_list(monthly, cols=["mes", "agendamentos", "horas"]),
        "agendamentos_rows": df.fillna("").to_dict(orient="records"),
    }


# =========================================================
# =============== VIEW HTML (INTERFACE) ===================
# =========================================================
@login_required
@permission_required("escola.view_relatorio", raise_exception=True)
def relatorio_conteudos(request):
    """
    Renderiza a página HTML com o formulário e as abas (Resumo / Por professor / Por conteúdo / Por aluno / Mensal).
    """
    form = RelatorioForm(request.GET or None)
    context = {"form": form}

    if form.is_valid():
        start = form.cleaned_data.get("start")
        end = form.cleaned_data.get("end")
        report = _generate_report_data(start, end)
        context.update(report)

        
        page = request.GET.get("page", 1)
        per_page = 25
        paginator = Paginator(context["agendamentos_rows"], per_page)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context["agendamentos_page"] = page_obj

    return render(request, "relatorio/relatorio_conteudos.html", context)


# =========================================================
# =============== ENDPOINT JSON (AJAX) ====================
# =========================================================
@login_required
@permission_required("escola.export_relatorio", raise_exception=True)
def relatorio_conteudos_json(request):
    """
    Retorna os dados do relatório em JSON — útil para chamadas AJAX que preencham as abas
    sem recarregar a página inteira.
    Parâmetros: start (YYYY-MM-DD), end (YYYY-MM-DD)
    """
    start_param = request.GET.get("start")
    end_param = request.GET.get("end")
    start_date = _parse_date(start_param)
    end_date = _parse_date(end_param)

    report = _generate_report_data(start_date, end_date)
    return JsonResponse(report, safe=False)


# =========================================================
# =============== EXPORTAÇÃO EXCEL (USANDO HELPER) ========
# =========================================================
@login_required
@permission_required("escola.view_agendamento", raise_exception=True)
def export_relatorio_excel(request):
    """
    Gera um arquivo Excel com múltiplas abas, reutilizando os mesmos cálculos do helper.
    Parâmetros: start (YYYY-MM-DD), end (YYYY-MM-DD)
    """
    start_param = request.GET.get("start")
    end_param = request.GET.get("end")
    start_date = _parse_date(start_param)
    end_date = _parse_date(end_param)

    # Reutiliza o helper para obter os dataframes/strutures
    # Precisamos recriar os DataFrames originais para salvar no Excel (usaremos os dados brutos)
    report_data = _generate_report_data(start_date, end_date)

    # Reconstruir DataFrames a partir das listas de dict (p/ escrita no Excel).
    # Observação: em projetos grandes pode ser melhor exportar direto do DF original.
    resumo_df = pd.DataFrame([report_data["resumo"]])
    by_prof_df = pd.DataFrame(report_data["by_professor"])
    by_aluno_df = pd.DataFrame(report_data["by_aluno"])
    by_conteudo_df = pd.DataFrame(report_data["by_conteudo"])
    monthly_df = pd.DataFrame(report_data["monthly"])

    # Agendamentos (rows)
    agendamentos_df = pd.DataFrame(report_data["agendamentos_rows"])
    # Garante colunas na ordem desejada
    desired_cols = [
        "id",
        "inicio",
        "duracao_minutos",
        "status",
        "aluno",
        "serie",
        "turma",
        "professor",
        "especialidade",
        "conteudo",
        "descritor",
    ]
    agendamentos_df = agendamentos_df.reindex(columns=desired_cols)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter", datetime_format="yyyy-mm-dd HH:MM") as writer:
        agendamentos_df.to_excel(writer, sheet_name="Agendamentos", index=False)
        resumo_df.to_excel(writer, sheet_name="Resumo", index=False)
        by_prof_df.to_excel(writer, sheet_name="Por Professor", index=False)
        by_aluno_df.to_excel(writer, sheet_name="Por Aluno", index=False)
        by_conteudo_df.to_excel(writer, sheet_name="Por Conteúdo", index=False)
        monthly_df.to_excel(writer, sheet_name="Mensal", index=False)

    buffer.seek(0)
    # Nome do arquivo com datas mais legíveis
    start_label = start_date or timezone.localdate()
    end_label = end_date or timezone.localdate()
    filename = f"relatorio_agendamentos_{start_label}_{end_label}.xlsx"

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
