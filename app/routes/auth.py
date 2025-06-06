from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models.usuarios import Usuario
from app.models.unidades import Unidade

auth_bp = Blueprint("auth", __name__)

# ─── Domínios internos permitidos ─────────────────────────
DOMINIOS_AUTORIZADOS = (
    "@kfp.com.br",
    "@kfp.net.br",
    "@grifcar.com.br",
)
# ───────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario or not usuario.senha_hash or not check_password_hash(usuario.senha_hash, senha):
            flash("E-mail ou senha inválidos.", "danger")
            return redirect(url_for("auth.login"))

        # Se não estiver ativo mas for domínio interno, auto-ativa
        dominio = "@" + email.split("@")[-1]
        if not usuario.ativo:
            if dominio in DOMINIOS_AUTORIZADOS:
                usuario.ativo = True
                db.session.commit()
                flash("Conta ativada automaticamente por domínio interno.", "info")
            else:
                flash("Sua conta ainda não foi ativada. Aguarde aprovação.", "warning")
                return redirect(url_for("auth.login"))

        # Faz o login na sessão
        session["usuario_id"]         = usuario.id
        session["usuario_nome"]       = usuario.nome
        session["usuario_tipo"]       = usuario.tipo
        session["usuario_unidade_id"] = usuario.unidade_id

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

        if Usuario.query.filter_by(email=email).first():
            flash("Este e-mail já está cadastrado.", "warning")
            return redirect(url_for("auth.cadastro"))

        try:
            unidade_obj = Unidade.query.get(int(unidade_id))
            if not unidade_obj:
                raise ValueError
        except ValueError:
            flash("Unidade inválida. Escolha novamente.", "danger")
            return redirect(url_for("auth.cadastro"))

        dominio = "@" + email.split("@")[-1]
        is_ativo = dominio in DOMINIOS_AUTORIZADOS

        hash_gerado = generate_password_hash(senha)

        novo = Usuario(
            nome              = nome,
            email             = email,
            senha_hash        = hash_gerado,
            tipo              = "solicitante",
            unidade_id        = unidade_obj.id,
            ativo             = is_ativo,
            google_id         = None,
            foto_url          = "/static/images/default_user.png",
            email_confirmado  = is_ativo,
            perfis            = "solicitante",
        )
        db.session.add(novo)
        db.session.commit()

        if is_ativo:
            flash("Cadastro realizado! Você já pode fazer login.", "success")
        else:
            flash("Cadastro realizado! Aguarde aprovação de um usuário autorizado.", "info")

        return redirect(url_for("auth.login"))

    unidades = Unidade.query.order_by(Unidade.nome).all()
    return render_template("auth/cadastro.html", unidades=unidades)
