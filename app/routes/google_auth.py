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

# monte o blueprint do Flask-Dance
google_bp = make_google_blueprint(
    client_id     = os.getenv("GOOGLE_CLIENT_ID"),
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET"),
    scope         = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    redirect_url  = "/login/google/callback"
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

    info      = resp.json()
    email     = info.get("email", "").lower()
    nome      = info.get("name", "")
    google_id = info.get("id")
    foto      = info.get("picture")

    # 1) tenta encontrar pelo google_id ou pelo email_principal
    usuario = Usuario.query.filter_by(google_id=google_id).first() \
           or Usuario.query.filter_by(email_principal=email).first()

    if usuario:
        # Atualiza dados de vinculação e imagem
        usuario.google_id    = google_id
        usuario.email_google = email
        usuario.foto_url     = foto or usuario.foto_url

        # Auto-ativa se domínio interno e ainda for pendente
        if usuario.status == Status.AGUARDANDO:
            dominio  = "@" + email.split("@")[-1]
            dominios = current_app.config.get("DOMINIOS_AUTORIZADOS", [])
            if dominio in dominios:
                usuario.status           = Status.ATIVO
                usuario.email_confirmado = True

        db.session.commit()

    else:
        # Cria novo usuário no primeiro login via Google
        dominio  = "@" + email.split("@")[-1]
        dominios = current_app.config.get("DOMINIOS_AUTORIZADOS", [])
        status   = Status.ATIVO if dominio in dominios else Status.AGUARDANDO

        usuario = Usuario(
            nome             = nome or email.split("@")[0],
            email_principal  = email,
            senha_hash       = None,
            google_id        = google_id,
            email_google     = email,
            tipo             = "solicitante",
            perfis           = "solicitante",
            unidade_id       = None,
            status           = status,
            email_confirmado = (status == Status.ATIVO),
            foto_url         = foto or "/static/images/default_user.png",
        )
        db.session.add(usuario)
        db.session.commit()

    # 2) só popula sessão se estiver ATIVO
    if usuario.status != Status.ATIVO:
        if usuario.status == Status.AGUARDANDO:
            # passo o email na query para preencher o formulário de ativação
            link = url_for("profile.request_activation", email=usuario.email_principal)
            msg  = Markup(
                "Sua conta está aguardando ativação. "
                f"<a href='{link}'>Clique aqui</a> se for funcionário autorizado."
            )
            flash(msg, "warning")
        else:
            flash("Conta desativada. Contate o administrador.", "danger")

        return redirect(url_for("auth.login"))

    # 3) popula sessão e segue normalmente
    session["usuario_id"]         = usuario.id
    session["usuario_nome"]       = usuario.nome
    session["usuario_tipo"]       = usuario.tipo
    session["usuario_perfis"]     = usuario.perfis
    session["usuario_unidade_id"] = usuario.unidade_id
    session["usuario_foto"]       = usuario.foto_url or url_for(
        "static", filename="images/default_user.png"
    )

    flash("Login via Google realizado com sucesso!", "success")
    return redirect(url_for("main.dashboard"))


@google_auth_bp.route("/google/unlink")
@login_required
def google_unlink():
    """
    Desvincula a conta Google do usuário logado.
    """
    usuario = Usuario.query.get(session["usuario_id"])
    usuario.google_id    = None
    usuario.email_google = None
    db.session.commit()
    flash("Conta Google desvinculada com sucesso.", "info")
    return redirect(url_for("profile.view"))
