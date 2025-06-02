document.addEventListener("DOMContentLoaded", function () {
    const container = document.getElementById("itens-container");
    const addButton = document.getElementById("add-item");

    // ✅ Verifica se os elementos existem na página
    if (!container || !addButton) return;

    // 🎯 Adiciona novo bloco de item ao formulário
    addButton.addEventListener("click", function (e) {
        e.preventDefault();

        const itemHTML = `
            <fieldset class="item-bloco">
                <legend>Item</legend>

                <label for="">Nome do Produto:
                    <input type="text" name="nome_produto[]" required class="maiusculo" placeholder="Ex: Impressora HP">
                </label><br>

                <label for="">Nome Técnico:
                    <input type="text" name="nome_tecnico[]" class="maiusculo" placeholder="Ex: HP LaserJet M140w">
                </label><br>

                <label for="">Quantidade:
                    <input type="number" name="quantidade[]" min="1" required>
                </label><br>

                <label for="">Voltagem:
                    <select name="voltagem[]">
                        <option value="">---</option>
                        <option value="110">110V</option>
                        <option value="220">220V</option>
                    </select>
                </label><br>

                <label for="">Especificações:
                    <textarea name="especificacoes[]" rows="2" class="maiusculo" placeholder="Detalhes técnicos..."></textarea>
                </label><br>

                <label for="">Link:
                    <input type="url" name="link[]" placeholder="https://...">
                </label><br>
            </fieldset>
        `;

        container.insertAdjacentHTML("beforeend", itemHTML);
    });

    // 🧠 Converte campos para maiúsculo enquanto o usuário digita
    document.addEventListener("input", function (e) {
        if (e.target.classList.contains("maiusculo")) {
            e.target.value = e.target.value.toUpperCase();
        }
    });
});
