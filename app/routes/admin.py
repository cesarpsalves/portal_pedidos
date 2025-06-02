from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from app.models.usuarios import Usuario
from app.extensions import db
from app.utils.auth import login_required

admin_bp = Blueprint("admin", __name__)

# Perfis que podem gerenciar permissões
PERFIS_GERENCIAIS = {"administrador", "gerente", "diretor"}


@admin_bp.route("/admin/usuarios")
@login_required
def gerenciar_usuarios():
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_GERENCIAIS:
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("exemplo.dashboard"))

    usuarios = Usuario.query.all()
    return render_template("admin/usuarios.html", usuarios=usuarios)


@admin_bp.route("/admin/atualizar_perfis", methods=["POST"])
@login_required
def atualizar_perfis():
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_GERENCIAIS:
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("exemplo.dashboard"))

    usuario_id = request.form.get("usuario_id")
    novos_perfis = request.form.getlist("perfis")

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("admin.gerenciar_usuarios"))

    # Atualiza os perfis como string separada por vírgula
    usuario.perfis = ",".join(novos_perfis)
    db.session.commit()

    flash(f"Perfis de {usuario.nome} atualizados com sucesso.", "success")
    return redirect(url_for("admin.gerenciar_usuarios"))
