import os
from functools import wraps
from markupsafe import Markup
from flask import (
    Blueprint, redirect, url_for, flash,
    session, current_app
)
from flask_dance.contrib.google import make_google_blueprint, google
from app.extensions import db
from app.models.usuarios import Usuario, Status

# Blueprint do Flask-Dance para autenticação Google
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    redirect_url="/login/google/callback"
)

google_auth_bp = Blueprint("google_auth", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("usuario_id"):
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@google_auth_bp.route("/login/google/callback")
def google_authorized():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Falha ao obter dados do Google.", "danger")
        return redirect(url_for("auth.login"))

    info = resp.json()
    email = info.get("email", "").lower()
    nome = info.get("name", "")
    google_id = info.get("id")
    foto = info.get("picture")

    # --- FLUXO 1: usuário já está logado, quer apenas vincular ---
    if "usuario_id" in session:
        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario:
            flash("Usuário não encontrado na sessão.", "danger")
            return redirect(url_for("auth.login"))

        # Verifica se esse google_id já está vinculado a outro usuário
        outro_usuario = Usuario.query.filter_by(google_id=google_id).first()
        if outro_usuario and outro_usuario.id != usuario.id:
            flash("Este e-mail do Google já está vinculado a outra conta.", "danger")
            return redirect(url_for("profile.view"))

        usuario.google_id = google_id
        usuario.email_google = email
        if usuario.foto_url in [None, '', '/static/images/default_user.png']:usuario.foto_url = foto

        db.session.commit()

        flash("Conta Google vinculada com sucesso!", "success")
        return redirect(url_for("profile.view"))

    # --- FLUXO 2: login/cadastro via Google ---
    usuario = Usuario.query.filter_by(google_id=google_id).first() \
           or Usuario.query.filter_by(email_principal=email).first()

    if usuario:
        usuario.google_id = google_id
        usuario.email_google = email
        if usuario.foto_url in [None, '', '/static/images/default_user.png']:usuario.foto_url = foto


        if usuario.status == Status.AGUARDANDO:
            dominio = "@" + email.split("@")[1]
            dominios = current_app.config.get("DOMINIOS_AUTORIZADOS", [])
            if dominio in dominios:
                usuario.status = Status.ATIVO
                usuario.email_confirmado = True

        db.session.commit()

    else:
        dominio = "@" + email.split("@")[1]
        dominios = current_app.config.get("DOMINIOS_AUTORIZADOS", [])
        status = Status.ATIVO if dominio in dominios else Status.AGUARDANDO

        usuario = Usuario(
            nome=nome or email.split("@")[0],
            email_principal=email,
            senha_hash=None,
            google_id=google_id,
            email_google=email,
            tipo="solicitante",
            perfis="solicitante",
            unidade_id=None,
            status=status,
            email_confirmado=(status == Status.ATIVO),
            foto_url=foto or "/static/images/default_user.png",
        )
        db.session.add(usuario)
        db.session.commit()

    if usuario.status != Status.ATIVO:
        if usuario.status == Status.AGUARDANDO:
            link = url_for("profile.request_activation", email=usuario.email_principal)
            msg = Markup(
                "Sua conta está aguardando ativação. "
                f"<a href='{link}'>Clique aqui</a> se for funcionário autorizado."
            )
            flash(msg, "warning")
        else:
            flash("Conta desativada. Contate o administrador.", "danger")
        return redirect(url_for("auth.login"))

    session["usuario_id"] = usuario.id
    session["usuario_nome"] = usuario.nome
    session["usuario_tipo"] = usuario.tipo
    session["usuario_perfis"] = usuario.perfis
    session["usuario_unidade_id"] = usuario.unidade_id
    session["usuario_status"]     = int(usuario.status)
    session["usuario_foto"] = usuario.foto_url or url_for(
        "static", filename="images/default_user.png"
    )

    flash("Login via Google realizado com sucesso!", "success")
    return redirect(url_for("main.dashboard"))


@google_auth_bp.route("/google/unlink")
@login_required
def google_unlink():
    usuario = Usuario.query.get(session["usuario_id"])
    usuario.google_id = None
    usuario.email_google = None
    db.session.commit()
    flash("Conta Google desvinculada com sucesso.", "info")
    return redirect(url_for("profile.view"))
