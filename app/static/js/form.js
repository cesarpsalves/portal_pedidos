// static/js/form.js

document.addEventListener("DOMContentLoaded", function () {
    const botaoAdicionar = document.getElementById("adicionarItem");
    const container = document.getElementById("items");
    const optRetirada = document.getElementById("opt-retirada");
    const optEntrega = document.getElementById("opt-entrega");
    const camposRetirada = document.getElementById("campos-retirada");
    const campoCPF = document.getElementById("cpf_retirada");
    const form = document.querySelector("form");

    // 1) Converte campos com class="maiusculo" para maiúsculo automaticamente
    document.addEventListener("input", function (e) {
        if (e.target.classList.contains("maiusculo")) {
            e.target.value = e.target.value.toUpperCase();
        }
    });

    // 2) Adiciona novo item responsivo
    botaoAdicionar?.addEventListener("click", function (e) {
        e.preventDefault();

        const row = document.createElement("div");
        row.classList.add("row", "g-2", "mb-2", "align-items-end");
        row.innerHTML = `
            <div class="col-12 col-md-3">
                <input type="text" name="nome_produto" class="form-control maiusculo" placeholder="Nome do Produto" list="produtos_sugeridos" autocomplete="off" spellcheck="false">
            </div>
            <div class="col-12 col-md-2">
                <input type="text" name="nome_tecnico" class="form-control maiusculo" placeholder="Nome Técnico" spellcheck="true">
            </div>
            <div class="col-6 col-md-1">
                <input type="text" name="quantidade" class="form-control" placeholder="Qtd">
            </div>
            <div class="col-6 col-md-2">
                <select name="voltagem" class="form-select">
                    <option value="">Voltagem</option>
                    <option value="110V">110V</option>
                    <option value="220V">220V</option>
                </select>
            </div>
            <div class="col-12 col-md-2">
                <input type="text" name="especificacoes" class="form-control maiusculo" placeholder="Especificações" spellcheck="true">
            </div>
            <div class="col-12 col-md-2">
                <input type="text" name="link" class="form-control" placeholder="Link">
            </div>
        `;

        container.appendChild(row);
    });

    // 3) Mostrar/Ocultar campos de Retirada
    function atualizarCamposRetirada() {
        const mostrar = optRetirada.checked;
        camposRetirada.style.display = mostrar ? "block" : "none";
        camposRetirada.querySelectorAll("input").forEach(input => {
            input.required = mostrar;
            input.disabled = !mostrar;
            if (!mostrar) input.value = "";
            removeMensagemErroCPF();
        });
    }

    optRetirada?.addEventListener("change", atualizarCamposRetirada);
    optEntrega?.addEventListener("change", atualizarCamposRetirada);
    atualizarCamposRetirada();

    // 4) Máscara de CPF com IMask
    if (window.IMask && campoCPF) {
        IMask(campoCPF, { mask: '000.000.000-00' });
    }

    // 5) Validação de CPF manual
    function validarCPFjs(cpf) {
        cpf = cpf.replace(/[^\d]+/g, '');
        if (cpf.length !== 11 || /^( )\1+$/.test(cpf)) return false;

        let soma = 0;
        for (let i = 0; i < 9; i++) soma += parseInt(cpf.charAt(i)) * (10 - i);
        let dig1 = (soma % 11 < 2) ? 0 : 11 - (soma % 11);
        if (dig1 !== parseInt(cpf.charAt(9))) return false;

        soma = 0;
        for (let i = 0; i < 10; i++) soma += parseInt(cpf.charAt(i)) * (11 - i);
        let dig2 = (soma % 11 < 2) ? 0 : 11 - (soma % 11);
        return dig2 === parseInt(cpf.charAt(10));
    }

    function mostrarMensagemErroCPF(msg) {
        removeMensagemErroCPF();
        const span = document.createElement("span");
        span.id = "erro-cpf-msg";
        span.className = "text-danger small";
        span.textContent = msg;
        campoCPF.parentNode.insertBefore(span, campoCPF.nextSibling);
    }

    function removeMensagemErroCPF() {
        const existente = document.getElementById("erro-cpf-msg");
        if (existente) existente.remove();
    }

    campoCPF?.addEventListener("blur", function () {
        const valor = campoCPF.value;
        if (!valor) return removeMensagemErroCPF();
        if (!validarCPFjs(valor)) {
            mostrarMensagemErroCPF("CPF inválido ou incompleto.");
        } else {
            removeMensagemErroCPF();
        }
    });

    // 6) Debug
    form?.addEventListener("submit", function () {
        const nome = document.querySelector("[name='nome_retirada']")?.value;
        const cpf = document.querySelector("[name='cpf_retirada']")?.value;
        console.log("DEBUG → Nome de retirada:", nome);
        console.log("DEBUG → CPF de retirada:", cpf);
    });
});
