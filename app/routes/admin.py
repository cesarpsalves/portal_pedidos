# app/routes/admin.py

from flask import (
    Blueprint, render_template, redirect, url_for, session, request, flash
)
from app.models.usuarios import Usuario
from app.extensions import db
from app.utils.auth import login_required

admin_bp = Blueprint("admin", __name__)

# Perfis que podem acessar esta página
PERFIS_GERENCIAIS = {"administrador", "gerente", "diretor"}

@admin_bp.route("/admin/usuarios")
@login_required
def gerenciar_usuarios():
    tipo_usuario = session.get("usuario_tipo")

    # Só certos papéis podem chegar aqui
    if tipo_usuario not in PERFIS_GERENCIAIS.union({"comprador", "aprovador"}):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("main.dashboard"))

    # Carrega todos os usuários para exibir na tabela
    usuarios = Usuario.query.order_by(Usuario.nome).all()

    # Monta, para quem está logado, quais perfis podem atribuir...
    if tipo_usuario == "comprador":
        allowed_perfis = ["solicitante", "comprador", "aprovador", "recebedor"]
    elif tipo_usuario == "aprovador":
        allowed_perfis = ["solicitante", "aprovador", "recebedor"]
    else:
        # administrador, gerente e diretor podem atribuir qualquer perfil
        allowed_perfis = [
            "solicitante",
            "aprovador",
            "comprador",
            "recebedor",
            "tributario",
            "financeiro",
            "administrador",
            "gerente",
            "diretor",
        ]

    # Agora montamos, também, quais tipos de usuário podem ser gerenciados
    if tipo_usuario == "comprador":
        permitted_user_types = {"solicitante", "comprador", "aprovador", "recebedor"}
    elif tipo_usuario == "aprovador":
        permitted_user_types = {"solicitante", "aprovador", "recebedor"}
    else:
        permitted_user_types = {
            "solicitante",
            "aprovador",
            "comprador",
            "recebedor",
            "tributario",
            "financeiro",
            "administrador",
            "gerente",
            "diretor",
        }

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios,
        allowed_perfis=allowed_perfis,
        permitted_user_types=permitted_user_types,
        meu_tipo=tipo_usuario,
    )

@admin_bp.route("/admin/atualizar_perfis", methods=["POST"])
@login_required
def atualizar_perfis():
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_GERENCIAIS.union({"comprador", "aprovador"}):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("main.dashboard"))

    usuario_id = request.form.get("usuario_id")
    novos_perfis = request.form.getlist("perfis")

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("admin.gerenciar_usuarios"))

    if tipo_usuario == "comprador":
        permitted = {"solicitante", "comprador", "aprovador", "recebedor"}
    elif tipo_usuario == "aprovador":
        permitted = {"solicitante", "aprovador", "recebedor"}
    else:
        permitted = {
            "solicitante",
            "aprovador",
            "comprador",
            "recebedor",
            "tributario",
            "financeiro",
            "administrador",
            "gerente",
            "diretor",
        }

    filtrados = [p for p in novos_perfis if p in permitted]
    usuario.perfis = ",".join(filtrados)
    db.session.commit()

    flash(f"Perfis de {usuario.nome} atualizados com sucesso.", "success")
    return redirect(url_for("admin.gerenciar_usuarios"))
