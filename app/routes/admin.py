# app/routes/admin.py
from flask import (
    Blueprint, render_template, redirect, url_for,
    session, request, flash
)
from app.models.usuarios import Usuario
from app.models.logs import Log
from app.models.unidades import Unidade
from app.models.solicitacoes import Solicitacao  # novo para checar vínculo
from app.extensions import db
from app.utils.auth import login_required, ativo_required, perfil_requerido

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/usuarios", methods=["GET"])
@login_required
@ativo_required
@perfil_requerido("administrador","gerente","diretor","comprador","aprovador","tributario","financeiro")
def gerenciar_usuarios():
    tipo_usuario = session["usuario_tipo"]
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    unidades = Unidade.query.order_by(Unidade.nome).all()

    if tipo_usuario == "comprador":
        allowed_perfis = ["solicitante","comprador","aprovador","recebedor"]
    elif tipo_usuario == "aprovador":
        allowed_perfis = ["solicitante","aprovador","recebedor"]
    else:
        allowed_perfis = [
            "solicitante","aprovador","comprador","recebedor",
            "tributario","financeiro","administrador","gerente","diretor"
        ]

    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios,
        unidades=unidades,
        allowed_perfis=allowed_perfis,
        meu_tipo=tipo_usuario,
    )

@admin_bp.route("/usuarios/atualizar", methods=["POST"])
@login_required
@ativo_required
@perfil_requerido("administrador","gerente","diretor","comprador","aprovador","tributario","financeiro")
def atualizar_usuario():
    usuario = Usuario.query.get(request.form["usuario_id"])
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("admin.gerenciar_usuarios"))

    tipo_usuario = session["usuario_tipo"]
    old = {
        "status": usuario.status,
        "unidade": usuario.unidade_id,
        "perfis": usuario.perfis,
        "tipo": usuario.tipo
    }

    if tipo_usuario in ["aprovador","comprador","tributario","financeiro", "gerente", "diretor", "administrador"]:
        unidade_id = request.form.get("unidade_id")
        if unidade_id and unidade_id.isdigit():
            usuario.unidade_id = int(unidade_id)

        status = request.form.get("status")
        if status is not None and status.isdigit():
            usuario.status = int(status)

    if tipo_usuario in ["gerente","diretor","administrador"]:
        perfis = request.form.getlist("perfis")
        if perfis:
            usuario.perfis = ",".join(perfis)
        if request.form.get("tipo"):
            usuario.tipo = request.form["tipo"]

    db.session.commit()

    changes = []
    if old["status"] != usuario.status:
        changes.append(f"status: {old['status']}→{usuario.status}")
    if old["unidade"] != usuario.unidade_id:
        changes.append(f"unidade: {old['unidade']}→{usuario.unidade_id}")
    if old["perfis"] != usuario.perfis:
        changes.append(f"perfis: {old['perfis']}→{usuario.perfis}")
    if old["tipo"] != usuario.tipo:
        changes.append(f"tipo: {old['tipo']}→{usuario.tipo}")

    if changes:
        log = Log(
            usuario_id=session["usuario_id"],
            acao=f"Atualizar usuário {usuario.nome}",
            descricao="; ".join(changes)
        )
        db.session.add(log)
        db.session.commit()

    flash(f"Usuário {usuario.nome} atualizado.", "success")
    return redirect(url_for("admin.gerenciar_usuarios"))

@admin_bp.route("/usuarios/excluir", methods=["POST"])
@login_required
@ativo_required
@perfil_requerido("administrador","gerente","diretor")
def excluir_usuario():
    usuario = Usuario.query.get(request.form["usuario_id"])
    if not usuario:
        flash("Usuário não encontrado.", "danger")
    else:
        solicitacoes = Solicitacao.query.filter_by(usuario_id=usuario.id).first()
        if solicitacoes:
            flash(f"Usuário {usuario.nome} não pode ser excluído pois possui solicitações vinculadas.", "danger")
            return redirect(url_for("admin.gerenciar_usuarios"))

        nome = usuario.nome
        db.session.delete(usuario)
        db.session.commit()
        log = Log(
            usuario_id=session["usuario_id"],
            acao="Excluir usuário",
            descricao=f"Usuário {nome} excluído"
        )
        db.session.add(log)
        db.session.commit()
        flash(f"Usuário {nome} excluído.", "warning")

    return redirect(url_for("admin.gerenciar_usuarios"))