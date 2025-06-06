# app/routes/google_auth.py

import os
from flask import Blueprint, redirect, url_for, flash, session, current_app
from flask_dance.contrib.google import make_google_blueprint, google
from app.extensions import db
from app.models.usuarios import Usuario

# ─── 1) CRIA O “BLUEPRINT” DO FLASK-DANCE PARA O GOOGLE ────────────────────────
#
#    • NÃO PASSE url_prefix AQUI (o próprio make_google_blueprint já define
#      internamente url_prefix="/login").
#
#    • Use "redirect_url" para apontar para a view de callback que você mesmo
#      vai criar logo abaixo (google_authorized).
#
google_bp = make_google_blueprint(
    client_id     = os.getenv("GOOGLE_CLIENT_ID"),
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET"),
    scope = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    # ← aqui usamos redirect_url em vez de redirect_to:
    redirect_url  = "/login/google/authorized"
)

# ─── 2) O NOSSO PRÓPRIO BLUEPRINT PARA TRATAR O CALLBACK "/login/google/authorized" ───
#
google_auth_bp = Blueprint("google_auth", __name__)

@google_auth_bp.route("/login/google/authorized")
def google_authorized():
    # Se não estiver autorizado pelo Google, redireciona ao fluxo de login do Flask-Dance:
    if not google.authorized:
        return redirect(url_for("google.login"))

    # Tentamos obter os dados básicos de perfil/email do Google:
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Falha ao obter dados do Google.", "danger")
        return redirect(url_for("auth.login"))

    info      = resp.json()
    email     = info.get("email", "").lower()
    nome      = info.get("name", "")
    google_id = info.get("id")
    foto      = info.get("picture")

    usuario = None
    # 3) Primeiramente, tenta encontrar usuário já cadastrado por google_id:
    if google_id:
        usuario = Usuario.query.filter_by(google_id=google_id).first()

    # 4) Se não encontrou por google_id, tenta por e-mail (para vincular contas manuais):
    if not usuario:
        usuario = Usuario.query.filter_by(email=email).first()

    if usuario:
        # 5) Se já existe, atualiza google_id e foto caso tenham mudado:
        usuario.google_id = google_id or usuario.google_id
        usuario.foto_url  = foto or usuario.foto_url

        # Se não está “ativo”, mas for domínio interno, ativa aqui:
        if not usuario.ativo:
            dominio = "@" + email.split("@")[-1]
            if dominio in current_app.config.get("DOMINIOS_AUTORIZADOS", []):
                usuario.ativo = True

        db.session.commit()
    else:
        # 6) Se não existe, cria um novo usuário “solicitante” ativado:
        novo = Usuario(
            nome             = nome or email.split("@")[0],
            email            = email,
            senha_hash       = None,  # Só login via Google
            google_id        = google_id,
            tipo             = "solicitante",
            ativo            = True,
            perfis           = "solicitante",
            foto_url         = foto or "/static/images/default_user.png",
            email_confirmado = True,   # via Google, consideramos já confirmado
        )
        db.session.add(novo)
        db.session.commit()
        usuario = novo

    # 7) Se, por algum motivo, o usuário ainda não estiver ativo (domínio bloqueado), bloqueia aqui:
    if not usuario.ativo:
        flash("Conta Google ainda não ativada.", "warning")
        return redirect(url_for("auth.login"))

    # 8) Por fim, grava dados na sessão e redireciona para o dashboard:
    session["usuario_id"]         = usuario.id
    session["usuario_nome"]       = usuario.nome
    session["usuario_tipo"]       = usuario.tipo
    session["usuario_unidade_id"] = usuario.unidade_id

    flash("Login via Google realizado com sucesso!", "success")
    return redirect(url_for("main.dashboard"))
