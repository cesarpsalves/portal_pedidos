document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const senha = document.getElementById("senha");
    const confirmar = document.getElementById("confirmar_senha");

    form.addEventListener("submit", function (e) {
        if (senha.value !== confirmar.value) {
            e.preventDefault();
            alert("As senhas não coincidem.");
        }
    });
});
