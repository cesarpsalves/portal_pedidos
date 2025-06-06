# app/routes/google_auth.py

import os
from flask import Blueprint, redirect, url_for, flash, session, current_app
from flask_dance.contrib.google import make_google_blueprint, google
from app.extensions import db
from app.models.usuarios import Usuario

# ─── 1) Cria o “blueprint” do Flask-Dance para o Google ────────────────────────────
#
#    • Não passe url_prefix aqui; o próprio make_google_blueprint já define "/login".
#    • Em vez de usar “redirect_to” (que conflita com o caminho "/authorized"),
#      vamos dizer explicitamente “redirect_url='/login/google/callback'”.
#    • O Google enviará o “code” para "/login/google/callback" depois que o usuário
#      der consentimento.
#
google_bp = make_google_blueprint(
    client_id     = os.getenv("GOOGLE_CLIENT_ID"),
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET"),
    scope = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    redirect_url  = "/login/google/callback"  # <—  colocar exatamente este URL de callback
)

# ─── 2) Nosso próprio blueprint, que agora trata “/login/google/callback” ──────────
#
google_auth_bp = Blueprint("google_auth", __name__)

@google_auth_bp.route("/login/google/callback")
def google_authorized():
    """
    Esta função será chamada depois que o Google redirecionar para
    /login/google/callback?state=…&code=….
    O Flask-Dance já deve ter trocado o 'code' por token.
    Se algo der errado (token não obtido), 'google.authorized' será False.
    """

    # ─── DEBUG: para entender se google.authorized == True ou False
    print(">>> DEBUG: google.authorized =", google.authorized)

    # 1) Se ainda não está autorizado (token não foi obtido ou está incorreto),
    #    retornamos ao fluxo de login do Flask-Dance, que vai para o Google novamente.
    if not google.authorized:
        resp = google.get("/oauth2/v2/userinfo")
        print(">>> DEBUG: resp.ok =", resp.ok)
        print(">>> DEBUG: resp.status_code =", resp.status_code)
        print(">>> DEBUG: resp.text[:200] =", resp.text[:200], "…")
        return redirect(url_for("google.login"))

    # ─── DEBUG: Se google.authorized == True, deveríamos ter o token na sessão
    print(">>> DEBUG: token armazenado em sessão =", session.get("google_oauth_token"))

    # 2) Agora, realmente buscamos o perfil do usuário no Google
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

    # 3) Se já existia um usuário com esse google_id, buscamos por google_id
    if google_id:
        usuario = Usuario.query.filter_by(google_id=google_id).first()

    # 4) Se não encontramos via google_id, tentamos achar pelo e-mail
    if not usuario:
        usuario = Usuario.query.filter_by(email=email).first()

    if usuario:
        # 5) Se achou um usuário já cadastrado, atualiza google_id/foto se necessário
        usuario.google_id = google_id or usuario.google_id
        usuario.foto_url  = foto or usuario.foto_url

        # Se não estava ativo, mas for domínio autorizado, ativa aqui:
        if not usuario.ativo:
            dominio = "@" + email.split("@")[-1]
            if dominio in current_app.config.get("DOMINIOS_AUTORIZADOS", []):
                usuario.ativo = True

        db.session.commit()
    else:
        # 6) Se não existe, cria um novo “solicitante” já ativo (login só via Google)
        novo = Usuario(
            nome             = nome or email.split("@")[0],
            email            = email,
            senha_hash       = None,  # sem senha, só login via Google
            google_id        = google_id,
            tipo             = "solicitante",
            ativo            = True,
            perfis           = "solicitante",
            foto_url         = foto or "/static/images/default_user.png",
            email_confirmado = True,  # validamos pela conta Google
        )
        db.session.add(novo)
        db.session.commit()
        usuario = novo

    # 7) Se, por algum motivo, o usuário ainda não estiver ativo
    if not usuario.ativo:
        flash("Conta Google ainda não ativada.", "warning")
        return redirect(url_for("auth.login"))

    # 8) Faz login de verdade: grava dados na sessão e redireciona ao dashboard
    session["usuario_id"]         = usuario.id
    session["usuario_nome"]       = usuario.nome
    session["usuario_tipo"]       = usuario.tipo
    session["usuario_unidade_id"] = usuario.unidade_id

    flash("Login via Google realizado com sucesso!", "success")
    return redirect(url_for("main.dashboard"))