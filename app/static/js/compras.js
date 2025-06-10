document.addEventListener("DOMContentLoaded", () => {
    const radioUnico = document.getElementById("entrega_unico");
    const radioMultiplo = document.getElementById("entrega_multiplo");
    const blocoUnico = document.getElementById("bloco-unico");
    const blocoMultiplo = document.getElementById("bloco-multiplo");
    const tabelaPacotesBody = document.querySelector("#tabela-pacotes tbody");
    const btnAdicionar = document.getElementById("btn-adicionar-pacote");
    let contadorPacote = 0;

    function atualizarBlocos() {
        blocoUnico.style.display = radioUnico.checked ? "block" : "none";
        blocoMultiplo.style.display = radioMultiplo.checked ? "block" : "none";
    }

    radioUnico.addEventListener("change", atualizarBlocos);
    radioMultiplo.addEventListener("change", atualizarBlocos);

    btnAdicionar.addEventListener("click", () => {
        contadorPacote += 1;
        const linha = document.createElement("tr");
        linha.innerHTML = `
      <td>${contadorPacote}</td>
      <td><input type="number" name="pacote_${contadorPacote}_qtd" min="1" required class="form-control"></td>
      <td><input type="text" name="pacote_${contadorPacote}_senha" class="form-control" placeholder="opcional"></td>
      <td><input type="date" name="pacote_${contadorPacote}_data" required class="form-control"></td>
      <td><input type="file" name="pacote_${contadorPacote}_nota" accept=".pdf,.jpg,.png" class="form-control"></td>
      <td><button type="button" class="btn btn-danger btn-sm btn-remover-pacote">Remover</button></td>
    `;
        tabelaPacotesBody.appendChild(linha);

        linha.querySelector(".btn-remover-pacote").addEventListener("click", () => {
            linha.remove();
        });
    });

    atualizarBlocos();
});