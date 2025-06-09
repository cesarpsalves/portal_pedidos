# app/utils/auth.py

from functools import wraps
from flask import session, redirect, url_for, flash
from app.models.usuarios import Status  # Enum com valores INATIVO = 0, AGUARDANDO = 1, ATIVO = 2

def login_required(f):
    """
    Exige que o usuário esteja logado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("usuario_id"):
            flash("Você precisa estar logado para acessar esta página.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def ativo_required(f):
    """
    Exige que o usuário esteja com a conta ativa (Status.ATIVO).
    """
    @wraps(f)
    def decorated_view(*args, **kwargs):
        status_usuario = session.get("usuario_status")
        try:
            if int(status_usuario) != Status.ATIVO:
                flash("Sua conta ainda não foi ativada. Aguarde aprovação.", "warning")
                return redirect(url_for("auth.login"))
        except (ValueError, TypeError):
            flash("Status de usuário inválido.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_view


def status_ativo_requerido(f):
    """
    Alternativa ao ativo_required para usar outro nome de decorador.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        status_usuario = session.get("usuario_status")
        try:
            if int(status_usuario) != Status.ATIVO:
                flash("Acesso negado. Sua conta está inativa.", "danger")
                return redirect(url_for("auth.login"))
        except (ValueError, TypeError):
            flash("Status de usuário inválido.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def perfil_requerido(*perfis_permitidos):
    """
    Exige que o usuário tenha pelo menos um dos perfis permitidos.
    Pode ser usado assim:
        @perfil_requerido("administrador")
        @perfil_requerido("comprador", "aprovador")
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            perfis_usuario = session.get("usuario_perfis", "")
            lista_perfis = [p.strip().lower() for p in perfis_usuario.split(",") if p.strip()]
            permitidos = [p.strip().lower() for p in perfis_permitidos]

            if not any(p in lista_perfis for p in permitidos):
                flash("Acesso restrito ao perfil: " + ", ".join(perfis_permitidos), "danger")
                return redirect(url_for("main.dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
