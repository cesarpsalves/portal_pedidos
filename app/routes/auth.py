# app/routes/auth.py

import os
from markupsafe import Markup
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message
from app.extensions import db, mail
from app.models.usuarios import Usuario, Status
from app.models.unidades import Unidade

auth_bp = Blueprint("auth", __name__)

DOMINIOS_PADRAO = (
    "@kfp.com.br",
    "@kfp.net.br",
    "@grifcar.com.br",
)

def gerar_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="senha-reset")

def validar_token(token, tempo_expiracao=1800):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="senha-reset", max_age=tempo_expiracao)
        return email
    except (SignatureExpired, BadSignature):
        return None

@auth_bp.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        usuario = Usuario.query.filter(
            or_(
                Usuario.email_principal == email,
                Usuario.email_empresa == email,
                Usuario.email_google == email
            )
        ).first()

        if not usuario:
            flash("E-mail não encontrado.", "danger")
            return redirect(url_for("auth.esqueci_senha"))

        token = gerar_token(email)
        link = url_for("auth.resetar_senha_token", token=token, _external=True)

        msg = Message("Redefinição de Senha - Portal KFP",
                      recipients=[email])
        msg.body = f"Olá, {usuario.nome}!\n\nClique no link abaixo para redefinir sua senha (válido por 30 minutos):\n{link}\n\nSe não solicitou isso, ignore este e-mail."

        mail.send(msg)
        flash("Um link de redefinição foi enviado para seu e-mail.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")

@auth_bp.route("/resetar-senha/<token>", methods=["GET", "POST"])
def resetar_senha_token(token):
    email = validar_token(token)
    if not email:
        flash("Link expirado ou inválido. Solicite um novo.", "danger")
        return redirect(url_for("auth.esqueci_senha"))

    usuario = Usuario.query.filter_by(email_principal=email).first()
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        senha = request.form.get("senha", "").strip()
        confirmar = request.form.get("confirmar_senha", "").strip()

        if senha != confirmar:
            flash("As senhas não coincidem.", "danger")
            return redirect(request.url)

        if len(senha) < 8:
            flash("A senha deve ter pelo menos 8 caracteres.", "danger")
            return redirect(request.url)

        usuario.senha_hash = generate_password_hash(senha)
        db.session.commit()

        flash("Senha redefinida com sucesso! Faça login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter(
            or_(
                Usuario.email_principal == email,
                Usuario.email_empresa == email,
                Usuario.email_google == email
            )
        ).first()

        if not usuario or not usuario.senha_hash or not check_password_hash(usuario.senha_hash, senha):
            flash("E-mail ou senha inválidos.", "danger")
            return redirect(url_for("auth.login"))

        dominios = current_app.config.get("DOMINIOS_AUTORIZADOS", DOMINIOS_PADRAO)
        dominio_email = "@" + email.split("@")[-1]

        if usuario.status == Status.AGUARDANDO and dominio_email in dominios:
            usuario.status = Status.ATIVO
            usuario.email_confirmado = True
            db.session.commit()
            flash("Conta ativada automaticamente por domínio interno.", "info")

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

        session["usuario_id"]         = usuario.id
        session["usuario_nome"]       = usuario.nome
        session["usuario_tipo"]       = usuario.tipo
        session["usuario_perfis"]     = usuario.perfis
        session["usuario_unidade_id"] = usuario.unidade_id
        session["usuario_status"]     = int(usuario.status)
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

        if Usuario.query.filter(
            or_(
                Usuario.email_principal == email,
                Usuario.email_empresa == email,
                Usuario.email_google == email
            )
        ).first():
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

@auth_bp.route("/definir-senha", methods=["GET", "POST"])
def definir_senha():
    if "usuario_id" not in session:
        flash("Você precisa estar logado para definir uma senha.", "danger")
        return redirect(url_for("auth.login"))

    usuario = Usuario.query.get(session["usuario_id"])

    if request.method == "POST":
        senha = request.form.get("senha", "").strip()
        confirmar = request.form.get("confirmar_senha", "").strip()

        if senha != confirmar:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for("auth.definir_senha"))

        if len(senha) < 8:
            flash("A senha deve ter pelo menos 8 caracteres.", "danger")
            return redirect(url_for("auth.definir_senha"))

        usuario.senha_hash = generate_password_hash(senha)
        db.session.commit()

        flash("Senha definida com sucesso!", "success")
        return redirect(url_for("profile.view"))

    return render_template("auth/set_password.html")

@auth_bp.route("/alterar-senha", methods=["GET", "POST"])
def alterar_senha():
    if "usuario_id" not in session:
        flash("Você precisa estar logado para alterar sua senha.", "danger")
        return redirect(url_for("auth.login"))

    usuario = Usuario.query.get(session["usuario_id"])

    if request.method == "POST":
        atual = request.form.get("senha_atual", "").strip()
        nova = request.form.get("nova_senha", "").strip()
        confirmar = request.form.get("confirmar_senha", "").strip()

        if not check_password_hash(usuario.senha_hash, atual):
            flash("Senha atual incorreta.", "danger")
            return redirect(url_for("auth.alterar_senha"))

        if nova != confirmar:
            flash("As novas senhas não coincidem.", "danger")
            return redirect(url_for("auth.alterar_senha"))

        if len(nova) < 8:
            flash("A nova senha deve ter pelo menos 8 caracteres.", "danger")
            return redirect(url_for("auth.alterar_senha"))

        usuario.senha_hash = generate_password_hash(nova)
        db.session.commit()

        flash("Senha alterada com sucesso!", "success")
        return redirect(url_for("profile.view"))

    return render_template("auth/change_password.html")
