from flask import (
    Blueprint, render_template, redirect, url_for, session, request, flash
)
from app.models.usuarios import Usuario
from app.models.logs import Log  # Adicionando o modelo de logs
from app.extensions import db
from app.utils.auth import login_required, ativo_required, perfil_requerido

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/usuarios")
@login_required
@ativo_required
@perfil_requerido("administrador", "gerente", "diretor", "comprador", "aprovador", "tributario", "financeiro")
def gerenciar_usuarios():
    tipo_usuario = session.get("usuario_tipo")
    usuarios = Usuario.query.order_by(Usuario.nome).all()

    if tipo_usuario == "comprador":
        allowed_perfis = ["solicitante", "comprador", "aprovador", "recebedor"]
    elif tipo_usuario == "aprovador":
        allowed_perfis = ["solicitante", "aprovador", "recebedor"]
    else:
        allowed_perfis = [
            "solicitante", "aprovador", "comprador", "recebedor",
            "tributario", "financeiro", "administrador", "gerente", "diretor"
        ]

    permitted_user_types = set(allowed_perfis)

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios,
        allowed_perfis=allowed_perfis,
        permitted_user_types=permitted_user_types,
        meu_tipo=tipo_usuario,
    )

@admin_bp.route("/admin/atualizar_perfis", methods=["POST"])
@login_required
@ativo_required
@perfil_requerido("administrador", "gerente", "diretor", "comprador", "aprovador")
def atualizar_perfis():
    tipo_usuario = session.get("usuario_tipo")
    usuario_id = request.form.get("usuario_id", "").strip()
    novos_perfis = request.form.getlist("perfis")
    nova_unidade = request.form.get("unidade_id", "").strip()
    novo_status = request.form.get("status", "").strip()

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("admin.gerenciar_usuarios"))

    # Lógica de alteração dos dados conforme o tipo de usuário
    old_status = usuario.status
    old_unidade = usuario.unidade_id
    old_perfis = usuario.perfis

    # Apenas certos usuários podem alterar o status e unidade
    if tipo_usuario in ["aprovador", "comprador", "tributario", "financeiro"]:
        usuario.unidade_id = nova_unidade
        usuario.status = novo_status
    elif tipo_usuario == "gerente":
        usuario.perfis = ",".join(novos_perfis)
        usuario.tipo = "gerente"
    elif tipo_usuario == "diretor":
        usuario.perfis = ",".join(novos_perfis)
        usuario.tipo = "diretor"

    db.session.commit()

    # Criando log da ação
    log_acao = f"Alteração de dados para {usuario.nome}"
    descricao = (
        f"Alterado status de {old_status} para {novo_status}, "
        f"unidade de {old_unidade} para {nova_unidade}, "
        f"perfis de {old_perfis} para {novos_perfis}."
    )
    log = Log(
        usuario_id=session["usuario_id"],
        acao=log_acao,
        descricao=descricao
    )
    db.session.add(log)
    db.session.commit()

    flash(f"Usuário {usuario.nome} atualizado com sucesso.", "success")
    return redirect(url_for("admin.gerenciar_usuarios"))
