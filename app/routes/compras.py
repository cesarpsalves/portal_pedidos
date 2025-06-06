# app/routes/compras.py

from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.models.solicitacoes import Solicitacao, ItemSolicitacao
from app.models.compras import Compra
from app.extensions import db
from app.utils.auth import login_required
from datetime import datetime

compras_bp = Blueprint("compras", __name__)

PERFIS_COMPRADOR = {"comprador", "administrador", "gerente", "diretor"}


@compras_bp.route("/compras")
@login_required
def lista_compras():
    """
    Lista todas as solicitações que estão no status 'aprovada'.
    O comprador deve clicar em "Ver Mais" para preencher os dados da compra.
    """
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_COMPRADOR:
        flash("Acesso negado.", "danger")
        return redirect(url_for("exemplo.dashboard"))

    solicitacoes_aprovadas = Solicitacao.query.filter_by(status="aprovada").all()
    return render_template("compras/lista.html", solicitacoes=solicitacoes_aprovadas)


@compras_bp.route("/compras/detalhes/<int:solicitacao_id>", methods=["GET", "POST"])
@login_required
def compra_detalhes(solicitacao_id):
    """
    Exibe todos os dados da solicitação e um formulário para preencher
    os detalhes da compra.
    Só ao submeter (POST) é que criamos as entradas em `compras`.
    """
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_COMPRADOR:
        flash("Acesso negado.", "danger")
        return redirect(url_for("exemplo.dashboard"))

    # Em GET: carrega a Solicitação (ela já existe) e mostra o formulário vazio
    solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
    itens = ItemSolicitacao.query.filter_by(solicitacao_id=solicitacao.id).all()

    if request.method == "POST":
        # 1) ler todos os campos vindos do formulário:
        forma_pagamento = request.form.get("forma_pagamento") or ""
        valor_total = request.form.get("valor_total") or "0"
        parcelamento = request.form.get("parcelamento") or None
        desconto = request.form.get("desconto") or "0"
        ultimos4 = request.form.get("ultimos4") or ""
        nome_loja = request.form.get("nome_loja") or ""
        inscricao_estadual = request.form.get("inscricao_estadual") or ""
        categoria_entrega = request.form.get("categoria_entrega") or "único"
        informacoes_adicionais = request.form.get("informacoes_adicionais") or ""
        data_prevista_entrega_str = request.form.get("data_prevista_entrega") or ""
        data_prevista_entrega = (
            datetime.strptime(data_prevista_entrega_str, "%Y-%m-%d").date()
            if data_prevista_entrega_str
            else None
        )

        # 2) para cada item dessa solicitação, vamos criar uma linha em Compra.
        #    Se preferir agrupar tudo em uma única tabela "Pedido", basta criar um registro intermediário,
        #    mas aqui seguimos o model atual de 'Compra' que é 1 compra ↔ 1 item.
        for item in itens:
            # ler senha de recebimento individual, se houver:
            senha_field = f"senha_recebimento_item_{item.id}"
            senha_recebimento = request.form.get(senha_field) or ""

            nova_compra = Compra(
                item_id=item.id,
                comprado_por=session.get("usuario_id"),
                valor_pago=valor_total,
                forma_pagamento=forma_pagamento,
                cartao_ultimos_digitos=ultimos4,
                valor_total=valor_total,
                parcelamento=int(parcelamento) if parcelamento else None,
                desconto=float(desconto),
                informacoes_adicionais=informacoes_adicionais,
                senha_recebimento=senha_recebimento,
                loja_nome=nome_loja,
                loja_inscricao_estadual=inscricao_estadual,
                entrega_categoria=categoria_entrega,
                data_prevista_entrega=data_prevista_entrega,
                data_compra=datetime.utcnow(),
            )
            db.session.add(nova_compra)

        # 3) depois de criar todas as linhas em Compra, atualiza o status da Solicitação para 'comprada':
        solicitacao.status = "comprada"
        db.session.commit()

        flash(
            f"Dados de compra cadastrados para a Solicitação #{solicitacao.id}.",
            "success",
        )
        return redirect(url_for("compras.lista_compras"))

    # GET: exibir template com dados da solicitação + itens + formulario vazio
    return render_template(
        "compras/detalhes.html",
        solicitacao=solicitacao,
        itens=itens,
    )
