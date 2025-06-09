// Função para exibir a prévia da imagem ao selecionar o arquivo
function previewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function () {
            const preview = document.getElementById('foto-preview');
            preview.src = reader.result;
        }
        reader.readAsDataURL(file);
    }
}
