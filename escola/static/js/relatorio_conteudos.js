document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("relatorio-form");
  const loading = document.getElementById("loading");
  const exportBtn = document.getElementById("export-btn");

  // Envio do formulário via AJAX
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const start = form.querySelector('[name="start"]').value;
    const end = form.querySelector('[name="end"]').value;

    if (!start || !end) {
      alert("Por favor, selecione o período inicial e final.");
      return;
    }

    gerarRelatorio(start, end);
  });

  // Função principal para buscar dados do relatório
  function gerarRelatorio(start, end) {
    loading.style.display = "block";

    fetch(`/relatorios/conteudos/json/?start=${start}&end=${end}`)
      .then((response) => response.json())
      .then((data) => {
        loading.style.display = "none";
        atualizarConteudo(data);
        exportBtn.href = `/relatorios/conteudos/export/?start=${start}&end=${end}`;
      })
      .catch((err) => {
        loading.style.display = "none";
        console.error("Erro ao gerar relatório:", err);
        alert("Erro ao gerar relatório. Tente novamente.");
      });
  }

  // Atualiza o conteúdo das abas com os dados retornados
  function atualizarConteudo(data) {
    // Aba Resumo
    const r = data.resumo;
    document.getElementById("resumo-content").innerHTML = `
      <div class="card card-body shadow-sm">
        <p><strong>Período:</strong> ${r.periodo_inicial} a ${r.periodo_final}</p>
        <p><strong>Total de Agendamentos:</strong> ${r.total_agendamentos}</p>
        <p><strong>Total de Horas:</strong> ${r.total_horas}</p>
        <p><strong>Média de Duração (min):</strong> ${r.media_duracao_min}</p>
      </div>
    `;

    // Abas de dados detalhados
    renderTabela("professor-content", data.by_professor, ["professor", "agendamentos", "horas"]);
    renderTabela("aluno-content", data.by_aluno, ["aluno", "agendamentos", "horas"]);
    renderTabela("conteudo-content", data.by_conteudo, ["conteudo", "agendamentos", "horas"]);
    renderTabela("mensal-content", data.monthly, ["mes", "agendamentos", "horas"]);
  }

  // Função genérica para renderizar tabelas dinâmicas
  function renderTabela(containerId, lista, colunas) {
    const container = document.getElementById(containerId);

    if (!lista || lista.length === 0) {
      container.innerHTML = "<p class='text-muted'>Sem dados disponíveis.</p>";
      return;
    }

    const thead = `
      <tr>${colunas.map(c => `<th>${c.toUpperCase()}</th>`).join("")}</tr>
    `;

    const tbody = lista
      .map(item => `
        <tr>${colunas.map(c => `<td>${item[c] ?? ""}</td>`).join("")}</tr>
      `)
      .join("");

    container.innerHTML = `
      <div class="table-responsive">
        <table class="table table-striped table-hover align-middle">
          <thead>${thead}</thead>
          <tbody>${tbody}</tbody>
        </table>
      </div>
    `;
  }
});
