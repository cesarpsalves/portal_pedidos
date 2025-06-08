# app/routes/auth.py
# Autenticação e cadastro de usuários

import os
from markupsafe import Markup
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models.usuarios import Usuario, Status
from app.models.unidades import Unidade

auth_bp = Blueprint("auth", __name__)

# Fallback se não estiver definido em config.py
DOMINIOS_PADRAO = (
    "@kfp.com.br",
    "@kfp.net.br",
    "@grifcar.com.br",
)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email_principal=email).first()
        if not usuario or not usuario.senha_hash or not check_password_hash(usuario.senha_hash, senha):
            flash("E-mail ou senha inválidos.", "danger")
            return redirect(url_for("auth.login"))

        dominios = current_app.config.get("DOMINIOS_AUTORIZADOS", DOMINIOS_PADRAO)
        dominio_email = "@" + email.split("@")[-1]

        # auto-ativa usuários pendentes de domínio interno
        if usuario.status == Status.AGUARDANDO and dominio_email in dominios:
            usuario.status = Status.ATIVO
            usuario.email_confirmado = True
            db.session.commit()
            flash("Conta ativada automaticamente por domínio interno.", "info")

        # bloqueia login se ainda não ativos ou inativos
        if usuario.status != Status.ATIVO:
            if usuario.status == Status.AGUARDANDO:
                link = url_for('profile.request_activation')
                msg = Markup(
                    "Sua conta está aguardando ativação. "
                    f"<a href='{link}'>Clique aqui</a> se for funcionário autorizado."
                )
                flash(msg, "warning")
            else:
                flash("Conta desativada. Contate o administrador.", "danger")
            return redirect(url_for("auth.login"))

        # popula sessão
        session["usuario_id"]         = usuario.id
        session["usuario_nome"]       = usuario.nome
        session["usuario_tipo"]       = usuario.tipo
        session["usuario_perfis"]     = usuario.perfis
        session["usuario_unidade_id"] = usuario.unidade_id
        session["usuario_foto"]       = usuario.foto_url or url_for(
            "static", filename="images/default_user.png"
        )

        flash("Login realizado com sucesso!", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logout realizado com sucesso.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome       = request.form.get("nome", "").strip()
        email      = request.form.get("email", "").strip().lower()
        senha      = request.form.get("senha", "")
        unidade_id = request.form.get("unidade_id")

        if not nome or not email or not senha or not unidade_id:
            flash("Todos os campos são obrigatórios.", "danger")
            return redirect(url_for("auth.cadastro"))

        if Usuario.query.filter_by(email_principal=email).first():
            flash("Este e-mail já está cadastrado.", "warning")
            return redirect(url_for("auth.cadastro"))

        try:
            unidade_obj = Unidade.query.get(int(unidade_id))
            if not unidade_obj:
                raise ValueError
        except ValueError:
            flash("Unidade inválida. Escolha novamente.", "danger")
            return redirect(url_for("auth.cadastro"))

        dominios = current_app.config.get("DOMINIOS_AUTORIZADOS", DOMINIOS_PADRAO)
        dominio_email = "@" + email.split("@")[-1]
        status = Status.ATIVO if dominio_email in dominios else Status.AGUARDANDO
        email_conf = status == Status.ATIVO

        novo = Usuario(
            nome             = nome,
            email_principal  = email,
            senha_hash       = generate_password_hash(senha),
            tipo             = "solicitante",
            perfis           = "solicitante",
            unidade_id       = unidade_obj.id,
            email_empresa    = None,
            email_google     = None,
            status           = status,
            email_confirmado = email_conf,
            foto_url         = "/static/images/default_user.png",
        )
        db.session.add(novo)
        db.session.commit()

        if status == Status.ATIVO:
            flash("Cadastro realizado! Já pode fazer login.", "success")
        else:
            flash("Cadastro realizado! Aguarde ativação do administrador.", "info")
        return redirect(url_for("auth.login"))

    unidades = Unidade.query.order_by(Unidade.nome).all()
    return render_template("auth/cadastro.html", unidades=unidades)
