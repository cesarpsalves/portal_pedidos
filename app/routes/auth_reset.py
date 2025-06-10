# app/routes/auth_reset.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.models.usuarios import Usuario
from app.extensions import db, mail
from flask_mail import Message
from werkzeug.security import generate_password_hash
from app.models.logs import Log
import datetime

reset_bp = Blueprint("auth_reset", __name__)


def gerar_token(email):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt="recuperar-senha")


def verificar_token(token, tempo_expiracao=1800):  # 30 minutos
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt="recuperar-senha", max_age=tempo_expiracao)
    except (SignatureExpired, BadSignature):
        return None
    return email


@reset_bp.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        usuario = Usuario.query.filter_by(email_principal=email).first()

        if not usuario:
            flash("E-mail não encontrado.", "danger")
            return redirect(url_for("auth_reset.esqueci_senha"))

        token = gerar_token(email)
        link = url_for("auth_reset.resetar_senha", token=token, _external=True)

        msg = Message("Redefinição de Senha – Portal KFP",
                      recipients=[email])
        msg.html = render_template("auth/email_reset.html", nome=usuario.nome, link=link)
        mail.send(msg)

        db.session.add(Log(usuario_id=usuario.id, acao="Esqueci Senha", descricao=f"Solicitou redefinição de senha para {email}"))
        db.session.commit()

        flash("Enviamos um link para redefinição de senha no seu e-mail.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


@reset_bp.route("/resetar-senha", methods=["GET", "POST"])
def resetar_senha():
    token = request.args.get("token")
    email = verificar_token(token)
    if not email:
        flash("Token inválido ou expirado.", "danger")
        return redirect(url_for("auth_reset.esqueci_senha"))

    usuario = Usuario.query.filter_by(email_principal=email).first()
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("auth_reset.esqueci_senha"))

    if request.method == "POST":
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar")

        if senha != confirmar:
            flash("As senhas não coincidem.", "danger")
            return redirect(request.url)
        if len(senha) < 8:
            flash("A senha deve ter ao menos 8 caracteres.", "danger")
            return redirect(request.url)

        usuario.senha_hash = generate_password_hash(senha)
        db.session.add(Log(usuario_id=usuario.id, acao="Redefinir Senha", descricao="Senha redefinida via token."))
        db.session.commit()

        flash("Senha redefinida com sucesso. Faça login com a nova senha.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", email=email)
