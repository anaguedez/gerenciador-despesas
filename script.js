function selecionarTema(nomeTema) {

    document.documentElement.setAttribute("data-tema", nomeTema);
    localStorage.setItem("tema", nomeTema);

}

function exibirToastSucesso() {

    const parametros = new URLSearchParams(window.location.search);
    const sucesso = parametros.get("sucesso");

    const mensagens = {
        cadastrado: "✅ Despesa cadastrada com sucesso!",
        atualizado: "✅ Despesa atualizada com sucesso!",
        excluido: "🗑️ Despesa excluída com sucesso!"
    };

    if (sucesso && mensagens[sucesso]) {

        document.getElementById("toastMensagem").textContent = mensagens[sucesso];

        const toast = new bootstrap.Toast(document.getElementById("toastSucesso"));
        toast.show();

        // Remove o parâmetro "sucesso" da URL para não exibir o toast de novo ao atualizar a página
        parametros.delete("sucesso");
        const novaUrl = window.location.pathname + (parametros.toString() ? "?" + parametros.toString() : "");
        window.history.replaceState({}, "", novaUrl);
    }

}

function ativarLoadingFormulario(idFormulario, idBotao, textoCarregando) {

    const formulario = document.getElementById(idFormulario);

    if (!formulario) {
        return;
    }

    formulario.addEventListener("submit", function () {

        const botao = document.getElementById(idBotao);

        botao.disabled = true;
        botao.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>' + textoCarregando;

    });

}

document.addEventListener("DOMContentLoaded", function () {

    exibirToastSucesso();
    ativarLoadingFormulario("formSalvar", "btnSalvar", "Salvando...");
    ativarLoadingFormulario("formAtualizar", "btnAtualizar", "Salvando...");

});

function renderizarGraficos(dados) {

    const cores = ["#6D28D9", "#2563EB", "#22C55E", "#FFD700", "#EF4444", "#F97316", "#06B6D4"];

    new Chart(document.getElementById("graficoCategoria"), {
        type: "pie",
        data: {
            labels: dados.categorias.labels,
            datasets: [{
                data: dados.categorias.valores,
                backgroundColor: cores
            }]
        }
    });

    new Chart(document.getElementById("graficoMensal"), {
        type: "bar",
        data: {
            labels: dados.mensal.labels,
            datasets: [{
                label: "Gasto mensal (R$)",
                data: dados.mensal.valores,
                backgroundColor: "#2563EB"
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } }
        }
    });

    new Chart(document.getElementById("graficoEvolucao"), {
        type: "line",
        data: {
            labels: dados.evolucao.labels,
            datasets: [{
                label: "Total acumulado (R$)",
                data: dados.evolucao.valores,
                borderColor: "#15803D",
                backgroundColor: "rgba(21, 128, 61, 0.2)",
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } }
        }
    });

}
