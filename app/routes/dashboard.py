# routes/dashboard.py

from flask import render_template, session
from app import app


@app.route("/dashboard")
def dashboard():
    # Captura as variáveis da sessão
    usuario_nome = session.get("usuario_nome")
    usuario_tipo = session.get("usuario_tipo")

    # Adiciona um print para verificar os dados
    print(f"Tipo de usuário: {usuario_tipo}")

    # Verifica se o tipo de usuário está correto e imprime no terminal
    if usuario_tipo is None:
        print("Erro: Tipo de usuário não encontrado na sessão!")

    # Renderiza o template com os dados
    return render_template(
        "dashboard.html", usuario_nome=usuario_nome, usuario_tipo=usuario_tipo
    )
