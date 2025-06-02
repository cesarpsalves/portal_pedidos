document.addEventListener("DOMContentLoaded", function () {
    const botaoAdicionar = document.getElementById("adicionarItem");
    const container = document.getElementById("items");
    const optRetirada = document.getElementById("opt-retirada");
    const optEntrega = document.getElementById("opt-entrega");
    const camposRetirada = document.getElementById("campos-retirada");
    const campoCPF = document.getElementById("cpf_retirada");

    // 🧩 Adiciona novo bloco de item ao formulário
    botaoAdicionar?.addEventListener("click", function () {
        const div = document.createElement("div");
        div.classList.add("item");
        div.innerHTML = `
            <input type="text" name="nome_produto" placeholder="Nome do Produto" class="maiusculo">
            <input type="text" name="nome_tecnico" placeholder="Nome Técnico" class="maiusculo">
            <input type="text" name="quantidade" placeholder="Qtd">
            <select name="voltagem" title="Voltagem">
                <option value="">Voltagem</option>
                <option value="110V">110V</option>
                <option value="220V">220V</option>
            </select>
            <input type="text" name="especificacoes" placeholder="Especificações" class="maiusculo">
            <input type="text" name="link" placeholder="Link">
        `;
        container.appendChild(div);
    });

    // 🧠 Converte campos com .maiusculo para letras maiúsculas
    document.addEventListener("input", function (e) {
        if (e.target.classList.contains("maiusculo")) {
            e.target.value = e.target.value.toUpperCase();
        }
    });

    // 🎯 Mostra ou oculta campos de retirada conforme escolha
    function atualizarCamposRetirada() {
        const mostrar = optRetirada.checked;
        camposRetirada.style.display = mostrar ? "block" : "none";

        // ✅ Garante apenas o visual e requerimento, sem desabilitar
        camposRetirada.querySelectorAll("input").forEach(input => {
            input.required = mostrar;
            input.disabled = false; // ⚠️ Certifique-se que está sempre habilitado!
        });
    }

    optRetirada?.addEventListener("change", atualizarCamposRetirada);
    optEntrega?.addEventListener("change", atualizarCamposRetirada);
    atualizarCamposRetirada();

    // 🧩 Máscara de CPF
    if (window.IMask && campoCPF) {
        IMask(campoCPF, {
            mask: '000.000.000-00'
        });
    }

    // 🧪 Debug: Verifica se os campos estão sendo enviados
    document.querySelector("form")?.addEventListener("submit", function () {
        const nome = document.querySelector("[name='nome_retirada']").value;
        const cpf = document.querySelector("[name='cpf_retirada']").value;
        console.log("⚠️ Enviando:", { nome, cpf });
    });

    document.querySelector("form").addEventListener("submit", function (e) {
        const nome = document.querySelector("[name='nome_retirada']").value;
        const cpf = document.querySelector("[name='cpf_retirada']").value;
        console.log("DEBUG → Nome retirada:", nome);
        console.log("DEBUG → CPF retirada:", cpf);
    });

});
