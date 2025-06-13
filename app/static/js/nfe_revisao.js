
console.log("✅ Script carregado com sucesso");

document.addEventListener("DOMContentLoaded", () => {
    const blocos = Array.from(document.querySelectorAll(".chave-bloco"));
    const campoChaveFinal = document.getElementById("chave_acesso_final");
    const btnConfirmar = document.getElementById("btn-confirmar");
    const alerta = document.getElementById("alerta-chave");
    const preview = document.getElementById("chave-preview");

    function atualizarChaveFinal() {
        const chave = blocos.map(b => b.value.trim()).join("");
        campoChaveFinal.value = chave;
        const formatada = blocos.map(b => b.value.padEnd(4, "-")).join(" ");
        preview.textContent = formatada;
        const preenchida = chave.length === 44 && blocos.every(b => b.value.length === 4);
        const valida = preenchida && validarChaveAcesso(chave);
        btnConfirmar.disabled = !valida;
        alerta.classList.toggle("d-none", valida);
    }

    function validarChaveAcesso(chave) {
        let peso = 2, soma = 0;
        for (let i = 42; i >= 0; i--) {
            soma += parseInt(chave[i]) * peso;
            peso = peso < 9 ? peso + 1 : 2;
        }
        const resto = soma % 11;
        const dv = (resto === 0 || resto === 1) ? 0 : 11 - resto;
        return parseInt(chave[43]) === dv;
    }

    blocos.forEach((bloco, i) => {
        bloco.addEventListener("input", e => {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 4);
            if (e.target.value.length === 4 && i < blocos.length - 1) {
                blocos[i + 1].focus();
            }
            atualizarChaveFinal();
        });
        bloco.addEventListener("keydown", e => {
            if (e.key === "Backspace" && bloco.value.length === 0 && i > 0) {
                blocos[i - 1].focus();
            }
        });
    });

    atualizarChaveFinal();
});
