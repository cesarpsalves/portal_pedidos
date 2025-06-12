// static/js/compras.js

document.addEventListener("DOMContentLoaded", () => {
    const entregaUnico = document.getElementById("entrega_unico");
    const entregaMultiplo = document.getElementById("entrega_multiplo");
    const blocoUnico = document.getElementById("bloco-unico");
    const blocoMultiplo = document.getElementById("bloco-multiplo");
    const tabelaPacotes = document.getElementById("tabela-pacotes").querySelector("tbody");
    const btnAdicionarPacote = document.getElementById("btn-adicionar-pacote");

    const toggleBlocosEntrega = () => {
        blocoUnico.style.display = entregaUnico.checked ? "block" : "none";
        blocoMultiplo.style.display = entregaMultiplo.checked ? "block" : "none";
    };

    entregaUnico.addEventListener("change", toggleBlocosEntrega);
    entregaMultiplo.addEventListener("change", toggleBlocosEntrega);
    toggleBlocosEntrega();

    let contadorPacote = 0;

    const adicionarLinhaPacote = (id, chave_acesso = null) => {
        const linha = document.createElement("tr");
        linha.innerHTML = `
            <td>${id}</td>
            <td><input type="number" name="pacotes[${id}][qtd]" class="form-control" required></td>
            <td><input type="text" name="pacotes[${id}][senha]" class="form-control"></td>
            <td><input type="date" name="pacotes[${id}][data_entrega]" class="form-control"></td>
            <td>
                <button type="button" class="btn btn-outline-info btn-anexar-nfe" data-pacote-id="${id}">
                    ${chave_acesso ? '✔️ Anexada' : 'Anexar Nota'}
                </button>
                <div class="nota-preview mt-1 small text-muted">
                    ${chave_acesso ? `<code>${chave_acesso}</code>` : ''}
                </div>
            </td>
            <td>
                <button type="button" class="btn btn-outline-danger btn-remover-pacote">Remover</button>
            </td>
        `;
        tabelaPacotes.appendChild(linha);
    };

    btnAdicionarPacote.addEventListener("click", () => {
        contadorPacote++;
        adicionarLinhaPacote(contadorPacote);
    });

    tabelaPacotes.addEventListener("click", (e) => {
        const target = e.target;

        if (target.classList.contains("btn-remover-pacote")) {
            target.closest("tr").remove();
        }

        if (target.classList.contains("btn-anexar-nfe")) {
            const pacoteId = target.dataset.pacoteId;
            if (pacoteId) {
                const solicitacaoId = window.solicitacaoId || "";
                window.location.href = `/compras/nfe/anexar/multiplo/${solicitacaoId}?pacote=${pacoteId}`;
            }
        }
    });

    if (window.sessionNotas) {
        for (const [id, chave] of Object.entries(window.sessionNotas)) {
            adicionarLinhaPacote(id, chave);
            contadorPacote = Math.max(contadorPacote, parseInt(id));
        }
    }
});
