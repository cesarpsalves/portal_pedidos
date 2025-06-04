# app/routes/solicitacoes.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.utils.auth import login_required
from app.extensions import db
from app.models.solicitacoes import Solicitacao, ItemSolicitacao
from app.models.unidades import Unidade
from app.models.empresas import Empresa

solicitacoes_bp = Blueprint("solicitacoes", __name__)


@solicitacoes_bp.route("/solicitacao/nova", methods=["GET", "POST"])
@login_required
def nova_solicitacao():
    if request.method == "POST":
        usuario_id = session.get("usuario_id")
        empresa_id = request.form.get("empresa_solicitante_id")
        finalidade = request.form.get("finalidade")
        centro_custo = request.form.get("centro_custo")
        unidade_id = request.form.get("unidade_id")
        tipo_recebimento = request.form.get("recebimento", "").upper()

        nome_retirada = (
            request.form.get("nome_retirada")
            if tipo_recebimento == "RETIRADA"
            else None
        )
        cpf_retirada = (
            request.form.get("cpf_retirada") if tipo_recebimento == "RETIRADA" else None
        )

        prazo_limite_str = request.form.get("prazo_limite")
        prazo_limite = (
            datetime.strptime(prazo_limite_str, "%Y-%m-%d")
            if prazo_limite_str
            else None
        )

        nova_solic = Solicitacao(
            usuario_id=usuario_id,
            empresa_solicitante_id=empresa_id,
            finalidade=finalidade,
            centro_custo=centro_custo,
            unidade_id=unidade_id,
            tipo_recebimento=tipo_recebimento,
            nome_retirada=nome_retirada,
            cpf_retirada=cpf_retirada,
            prazo_limite=prazo_limite,
            status="pendente",
        )
        db.session.add(nova_solic)
        db.session.flush()  # para obter nova_solic.id

        # Itens da solicitação
        nomes = request.form.getlist("nome_produto")
        tecnicos = request.form.getlist("nome_tecnico")
        quantidades = request.form.getlist("quantidade")
        voltagens = request.form.getlist("voltagem")
        especificacoes = request.form.getlist("especificacoes")
        links = request.form.getlist("link")

        for i in range(len(nomes)):
            if nomes[i].strip():
                item = ItemSolicitacao(
                    solicitacao_id=nova_solic.id,
                    nome_produto=nomes[i],
                    nome_tecnico=tecnicos[i] if i < len(tecnicos) else "",
                    quantidade=(
                        int(quantidades[i])
                        if i < len(quantidades) and quantidades[i].isdigit()
                        else 1
                    ),
                    voltagem=voltagens[i] if i < len(voltagens) else "",
                    especificacoes=especificacoes[i] if i < len(especificacoes) else "",
                    link=links[i] if i < len(links) else "",
                )
                db.session.add(item)

        db.session.commit()
        flash("Solicitação criada com sucesso!", "success")
        return redirect(url_for("exemplo.dashboard"))

    empresas = Empresa.query.order_by(Empresa.nome).all()
    unidades = Unidade.query.order_by(Unidade.nome).all()
    hoje = datetime.utcnow().date().strftime("%Y-%m-%d")
    dias_max = 30

    return render_template(
        "solicitacoes/nova.html",
        empresas=empresas,
        unidades=unidades,
        hoje=hoje,
        dias_max=dias_max,
    )


@solicitacoes_bp.route("/solicitacoes")
@login_required
def lista_solicitacoes():
    usuario_id = session.get("usuario_id")
    tipo_usuario = session.get("usuario_tipo")

    if tipo_usuario == "administrador":
        solicitacoes = (
            Solicitacao.query
            .options(joinedload(Solicitacao.itens))
            .order_by(Solicitacao.criado_em.desc())
            .all()
        )
    else:
        solicitacoes = (
            Solicitacao.query
            .options(joinedload(Solicitacao.itens))
            .filter_by(usuario_id=usuario_id)
            .order_by(Solicitacao.criado_em.desc())
            .all()
        )

    return render_template("solicitacoes/lista.html", solicitacoes=solicitacoes)


@solicitacoes_bp.route("/solicitacao/<int:id>")
@login_required
def ver_solicitacao(id):
    solicitacao = Solicitacao.query.get_or_404(id)

    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario != "administrador" and solicitacao.usuario_id != session.get("usuario_id"):
        flash("Acesso negado.", "danger")
        return redirect(url_for("solicitacoes.lista_solicitacoes"))

    itens = ItemSolicitacao.query.filter_by(solicitacao_id=solicitacao.id).all()
    anexos = solicitacao.anexos

    return render_template(
        "solicitacoes/ver.html", solicitacao=solicitacao, itens=itens, anexos=anexos
    )
