# app/routes/aprovacoes.py

from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.models.solicitacoes import Solicitacao, ItemSolicitacao
from app.extensions import db
from app.utils.auth import login_required, ativo_required

aprovacoes_bp = Blueprint("aprovacoes", __name__)

PERFIS_APROVACAO = {"aprovador", "administrador", "gerente", "diretor"}


@aprovacoes_bp.route("/aprovacoes")
@login_required
@ativo_required
def listar_solicitacoes():
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_APROVACAO:
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("main.dashboard"))

    solicitacoes_pendentes = (
        Solicitacao.query.filter_by(status="pendente")
        .order_by(Solicitacao.criado_em.desc())
        .all()
    )
    return render_template("aprovacoes/lista.html", solicitacoes=solicitacoes_pendentes)


@aprovacoes_bp.route("/aprovacoes/aprovar/<int:id>", methods=["POST"])
@login_required
@ativo_required
def aprovar_solicitacao(id):
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_APROVACAO:
        flash("Você não tem permissão para aprovar.", "danger")
        return redirect(url_for("main.dashboard"))

    solicitacao = Solicitacao.query.get_or_404(id)
    solicitacao.status = "aprovada"
    solicitacao.observacao = None
    db.session.commit()

    flash(f"Solicitação #{id} aprovada com sucesso.", "success")
    return redirect(url_for("aprovacoes.listar_solicitacoes"))


@aprovacoes_bp.route("/aprovacoes/rejeitar/<int:id>", methods=["POST"])
@login_required
@ativo_required
def rejeitar_solicitacao(id):
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_APROVACAO:
        flash("Você não tem permissão para rejeitar.", "danger")
        return redirect(url_for("main.dashboard"))

    motivo = request.form.get("motivo")
    if not motivo:
        flash("Informe o motivo da rejeição.", "warning")
        return redirect(url_for("aprovacoes.listar_solicitacoes"))

    solicitacao = Solicitacao.query.get_or_404(id)
    solicitacao.status = "rejeitada"
    solicitacao.observacao = motivo
    db.session.commit()

    flash(f"Solicitação #{id} rejeitada com sucesso.", "info")
    return redirect(url_for("aprovacoes.listar_solicitacoes"))


@aprovacoes_bp.route("/aprovacoes/detalhes/<int:solicitacao_id>", methods=["GET", "POST"])
@login_required
@ativo_required
def detalhes_solicitacao(solicitacao_id):
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_APROVACAO:
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("main.dashboard"))

    solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
    itens = ItemSolicitacao.query.filter_by(solicitacao_id=solicitacao.id).all()
    anexos = solicitacao.anexos

    if request.method == "POST":
        acao = request.form.get("acao")
        if acao == "aprovar":
            solicitacao.status = "aprovada"
            solicitacao.observacao = None
            db.session.commit()
            flash(f"Solicitação #{solicitacao.id} aprovada com sucesso.", "success")
            return redirect(url_for("aprovacoes.listar_solicitacoes"))

        elif acao == "rejeitar":
            motivo = request.form.get("motivo_rejeicao")
            if not motivo:
                flash("Por favor, forneça o motivo da rejeição.", "warning")
            else:
                solicitacao.status = "rejeitada"
                solicitacao.observacao = motivo
                db.session.commit()
                flash(f"Solicitação #{solicitacao.id} rejeitada.", "info")
                return redirect(url_for("aprovacoes.listar_solicitacoes"))

    return render_template(
        "aprovacoes/detalhes.html", solicitacao=solicitacao, itens=itens, anexos=anexos
    )
