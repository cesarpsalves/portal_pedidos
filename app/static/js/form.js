// static/js/form.js

document.addEventListener("DOMContentLoaded", function () {
    const botaoAdicionar = document.getElementById("adicionarItem");
    const container = document.getElementById("items");
    const optRetirada = document.getElementById("opt-retirada");
    const optEntrega = document.getElementById("opt-entrega");
    const camposRetirada = document.getElementById("campos-retirada");
    const campoCPF = document.getElementById("cpf_retirada");
    const form = document.querySelector("form");

    // 1) Função para converter campos com class="maiusculo" em maiúsculas automaticamente
    document.addEventListener("input", function (e) {
        if (e.target.classList.contains("maiusculo")) {
            e.target.value = e.target.value.toUpperCase();
        }
    });

    // 2) Adicionar novo bloco de item ao clicar no botão
    botaoAdicionar?.addEventListener("click", function (e) {
        e.preventDefault();
        const div = document.createElement("div");
        div.classList.add("item");
        div.innerHTML = `
            <input type="text" name="nome_produto" placeholder="Nome do Produto" class="maiusculo" list="produtos_sugeridos" autocomplete="off" spellcheck="false">
            <input type="text" name="nome_tecnico" placeholder="Nome Técnico" class="maiusculo" spellcheck="true">
            <input type="text" name="quantidade" placeholder="Qtd">
            <select name="voltagem" title="Voltagem">
                <option value="">Voltagem</option>
                <option value="110V">110V</option>
                <option value="220V">220V</option>
            </select>
            <input type="text" name="especificacoes" placeholder="Especificações" class="maiusculo" spellcheck="true">
            <input type="text" name="link" placeholder="Link">
        `;
        container.appendChild(div);
    });

    // 3) Mostrar/Ocultar campos de Retirada e configurar required
    function atualizarCamposRetirada() {
        const mostrar = optRetirada.checked;
        camposRetirada.style.display = mostrar ? "block" : "none";
        camposRetirada.querySelectorAll("input").forEach(input => {
            if (mostrar) {
                input.required = true;
                input.disabled = false;
            } else {
                input.required = false;
                input.value = "";  // limpa valor
                input.disabled = true;
                removeMensagemErroCPF();
            }
        });
    }

    optRetirada?.addEventListener("change", atualizarCamposRetirada);
    optEntrega?.addEventListener("change", atualizarCamposRetirada);
    atualizarCamposRetirada(); // inicializa no carregamento

    // 4) Máscara de CPF com IMask, se disponível
    if (window.IMask && campoCPF) {
        IMask(campoCPF, { mask: '000.000.000-00' });
    }

    // 5) Validação de CPF em JS (ao sair do campo)
    function validarCPFjs(cpf) {
        cpf = cpf.replace(/[^\d]+/g, '');
        if (cpf.length !== 11) return false;
        if (/^(\d)\1{10}$/.test(cpf)) return false;

        let soma = 0;
        for (let i = 0; i < 9; i++) {
            soma += parseInt(cpf.charAt(i)) * (10 - i);
        }
        let resto = soma % 11;
        let dig1 = resto < 2 ? 0 : 11 - resto;
        if (dig1 !== parseInt(cpf.charAt(9))) return false;

        soma = 0;
        for (let i = 0; i < 10; i++) {
            soma += parseInt(cpf.charAt(i)) * (11 - i);
        }
        resto = soma % 11;
        let dig2 = resto < 2 ? 0 : 11 - resto;
        return dig2 === parseInt(cpf.charAt(10));
    }

    function mostrarMensagemErroCPF(msg) {
        removeMensagemErroCPF();
        const span = document.createElement("span");
        span.id = "erro-cpf-msg";
        span.style.color = "red";
        span.style.fontSize = "0.9em";
        span.textContent = msg;
        campoCPF.parentNode.insertBefore(span, campoCPF.nextSibling);
    }

    function removeMensagemErroCPF() {
        const existente = document.getElementById("erro-cpf-msg");
        if (existente) existente.remove();
    }

    campoCPF?.addEventListener("blur", function () {
        const valor = campoCPF.value;
        if (!valor) {
            removeMensagemErroCPF();
            return;
        }
        if (!validarCPFjs(valor)) {
            mostrarMensagemErroCPF("CPF inválido ou incompleto.");
        } else {
            removeMensagemErroCPF();
        }
    });

    // 6) Debug: Exibir no console se nome_retirada e cpf_retirada chegaram no submit
    form?.addEventListener("submit", function () {
        const nome = document.querySelector("[name='nome_retirada']")?.value;
        const cpf = document.querySelector("[name='cpf_retirada']")?.value;
        console.log("DEBUG → Nome de retirada:", nome);
        console.log("DEBUG → CPF de retirada:", cpf);
    });
});
