# app/routes/historico.py

from flask import Blueprint, render_template, request, session, redirect, url_for
from app.extensions import db
from app.models.solicitacoes import Solicitacao
from app.utils.auth import login_required
from datetime import datetime

historico_bp = Blueprint("historico", __name__)


@historico_bp.route("/historico")
@login_required
def historico_solicitacoes():
    usuario_id = session.get("usuario_id")
    tipo_usuario = session.get("usuario_tipo")

    status = request.args.get("status")
    data_str = request.args.get("data")
    data = None
    if data_str:
        try:
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            data = None

    query = Solicitacao.query

    if tipo_usuario != "administrador":
        query = query.filter_by(usuario_id=usuario_id)

    if status:
        query = query.filter(Solicitacao.status == status.lower())

    if data:
        query = query.filter(db.func.date(Solicitacao.criado_em) == data)

    solicitacoes = query.order_by(Solicitacao.criado_em.desc()).all()

    return render_template(
        "historico/lista.html", solicitacoes=solicitacoes, status=status, data=data_str
    )
