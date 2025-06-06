# app/routes/aprovacoes.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.models.solicitacoes import Solicitacao
from app.models.usuarios import Usuario
from app.extensions import db
from app.utils.auth import login_required

aprovacoes_bp = Blueprint("aprovacoes", __name__)

# Perfis autorizados a aprovar ou rejeitar
PERFIS_APROVACAO = {"aprovador", "administrador", "gerente", "diretor"}


@aprovacoes_bp.route("/aprovacoes")
@login_required
def lista_aprovacoes():
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_APROVACAO:
        flash("Acesso negado.", "danger")
        return redirect(url_for("exemplo.dashboard"))

    solicitacoes_pendentes = Solicitacao.query.filter_by(status="pendente").all()
    return render_template("aprovacoes/lista.html", solicitacoes=solicitacoes_pendentes)


@aprovacoes_bp.route("/aprovacoes/aprovar/<int:id>", methods=["POST"])
@login_required
def aprovar_solicitacao(id):
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_APROVACAO:
        flash("Você não tem permissão para aprovar.", "danger")
        return redirect(url_for("exemplo.dashboard"))

    solicitacao = Solicitacao.query.get_or_404(id)
    solicitacao.status = "aprovada"
    solicitacao.observacao = None
    db.session.commit()
    flash(f"Solicitação #{id} aprovada com sucesso.", "success")
    return redirect(url_for("aprovacoes.lista_aprovacoes"))


@aprovacoes_bp.route("/aprovacoes/rejeitar/<int:id>", methods=["POST"])
@login_required
def rejeitar_solicitacao(id):
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_APROVACAO:
        flash("Você não tem permissão para rejeitar.", "danger")
        return redirect(url_for("exemplo.dashboard"))

    motivo = request.form.get("motivo")
    if not motivo:
        flash("Informe o motivo da rejeição.", "warning")
        return redirect(url_for("aprovacoes.lista_aprovacoes"))

    solicitacao = Solicitacao.query.get_or_404(id)
    solicitacao.status = "rejeitada"
    solicitacao.observacao = motivo
    db.session.commit()
    flash(f"Solicitação #{id} rejeitada com sucesso.", "info")
    return redirect(url_for("aprovacoes.lista_aprovacoes"))
