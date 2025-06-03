from flask import Blueprint, render_template, session
from app.utils.auth import login_required

exemplo_bp = Blueprint("exemplo", __name__)

# Rota pública de entrada
@exemplo_bp.route("/")
def home():
    return render_template("home.html")

# Rota protegida (dashboard)
@exemplo_bp.route("/dashboard")
@login_required
def dashboard():
    usuario_nome = session.get("usuario_nome")
    return render_template("dashboard.html", usuario_nome=usuario_nome)

