# app/routes/main.py

from flask import Blueprint, render_template, session
from app.utils.auth import login_required, ativo_required

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/dashboard")
@login_required
@ativo_required
def dashboard():
    usuario_nome = session.get("usuario_nome")
    return render_template("dashboard.html", usuario_nome=usuario_nome)
