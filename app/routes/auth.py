from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models.usuarios import Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        # Verifica se o usuário existe no banco de dados
        usuario = Usuario.query.filter_by(email=email).first()

        # Verifica se a senha fornecida é correta
        if usuario and check_password_hash(usuario.senha_hash, senha):
            # Se estiver correto, armazena as informações na sessão
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            session["usuario_tipo"] = usuario.tipo  # Armazena o tipo de usuário
            flash("Login realizado com sucesso!", "success")
            return redirect(
                url_for("exemplo.dashboard")
            )  # Redireciona para o dashboard
        else:
            flash("E-mail ou senha inválidos.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    # Limpa a sessão quando o usuário sai
    session.clear()
    flash("Logout realizado com sucesso.", "info")
    return redirect(url_for("auth.login"))
