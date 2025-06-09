# routes/dashboard.py

from flask import render_template, session, redirect, url_for, flash
from app import app
from app.utils.auth import login_required, ativo_required

@app.route("/dashboard")
@login_required
@ativo_required
def dashboard():
    usuario_nome = session.get("usuario_nome")
    usuario_tipo = session.get("usuario_tipo")

    if usuario_tipo is None:
        flash("Erro: Tipo de usuário não encontrado na sessão.", "danger")
        return redirect(url_for("main.home"))

    return render_template(
        "dashboard.html", usuario_nome=usuario_nome, usuario_tipo=usuario_tipo
    )
