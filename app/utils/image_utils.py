from PIL import Image
import os

# Função para verificar se o arquivo é uma imagem válida
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para redimensionar a imagem
def resize_image(image_file, target_size=(200, 200)):
    """Redimensiona a imagem para o tamanho alvo (padrão: 200x200)."""
    image = Image.open(image_file)
    image = image.resize(target_size)  # Redimensiona a imagem
    return image
