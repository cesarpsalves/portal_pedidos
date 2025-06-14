
from flask import (
    Blueprint, render_template, redirect, url_for, session, flash, request,
    send_file, current_app, jsonify, abort
)
from flask_wtf import FlaskForm
from wtforms import HiddenField
from app.models.solicitacoes import Solicitacao, ItemSolicitacao
from app.models.compras import Compra
from app.models.notas_fiscais import NotaFiscal
from app.models.pacotes import PacoteEntrega
from app.extensions import db
from app.utils.auth import login_required, ativo_required
from app.utils.nfe_utils import (
    extrair_dados_pdf, extrair_texto_pdf_pypdf2,
    salvar_texto_temporario, extrair_chave_acesso
)
from app.utils.nfeio_api import consultar_nfe_nfeio
from datetime import datetime
import os
import uuid

compras_bp = Blueprint("compras", __name__)

PERFIS_COMPRADOR = {"comprador", "administrador", "gerente", "diretor"}

class DummyForm(FlaskForm):
    csrf_token = HiddenField()



@compras_bp.route("/compras")
@login_required
@ativo_required
def lista_compras():
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_COMPRADOR:
        flash("Acesso negado.", "danger")
        return redirect(url_for("main.dashboard"))

    solicitacoes_aprovadas = Solicitacao.query.filter_by(status="aprovada").all()
    return render_template("compras/lista.html", solicitacoes=solicitacoes_aprovadas)


@compras_bp.route("/compras/detalhes/<int:solicitacao_id>", methods=["GET", "POST"])
@login_required
@ativo_required
def compra_detalhes(solicitacao_id):
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in PERFIS_COMPRADOR:
        flash("Acesso negado.", "danger")
        return redirect(url_for("main.dashboard"))

    solicitacao = Solicitacao.query.get_or_404(solicitacao_id)
    itens = ItemSolicitacao.query.filter_by(solicitacao_id=solicitacao.id).all()

    if request.method == "POST":
        forma_pagamento = request.form.get("forma_pagamento") or ""
        valor_total = request.form.get("valor_total") or "0"
        parcelamento = request.form.get("parcelamento") or None
        desconto = request.form.get("desconto") or "0"
        ultimos4 = request.form.get("ultimos4") or ""
        nome_loja = request.form.get("nome_loja") or ""
        inscricao_estadual = request.form.get("inscricao_estadual") or ""
        categoria_entrega = request.form.get("categoria_entrega") or "único"
        informacoes_adicionais = request.form.get("informacoes_adicionais") or ""

        for item in itens:
            senha_field = f"senha_recebimento_item_{item.id}"
            senha_recebimento = request.form.get(senha_field) or request.form.get("senha_recebimento_unico") or ""

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
                data_compra=datetime.utcnow()
            )
            db.session.add(nova_compra)
            db.session.flush()

            if categoria_entrega == "unico":
                data_entrega_str = request.form.get("data_prevista_entrega_unico") or ""
                data_entrega = datetime.strptime(data_entrega_str, "%Y-%m-%d").date() if data_entrega_str else None

                dados_nfe = session.pop(f"nfe_temporaria_unico_{solicitacao_id}", None)
                nota_fiscal = None

                if dados_nfe:
                    nota_fiscal = NotaFiscal(
                        chave_acesso=dados_nfe.get("chave_acesso"),
                        arquivo_pdf=dados_nfe.get("arquivo_pdf"),
                        criado_por=session.get("usuario_id")
                    )
                    db.session.add(nota_fiscal)
                    db.session.flush()

                pacote = PacoteEntrega(
                    compra_id=nova_compra.id,
                    quantidade=1,
                    senha_recebimento=senha_recebimento,
                    data_prevista_entrega=data_entrega,
                    nota_fiscal_id=nota_fiscal.id if nota_fiscal else None,
                )
                db.session.add(pacote)

            elif categoria_entrega == "multiplo":
                for i in range(1, 100):
                    qtd = request.form.get(f"pacotes[{i}][qtd]")
                    senha = request.form.get(f"pacotes[{i}][senha]")
                    data = request.form.get(f"pacotes[{i}][data_entrega]")

                    if not qtd and not senha and not data:
                        continue

                    data_entrega = datetime.strptime(data, "%Y-%m-%d").date() if data else None
                    dados_nfe = session.pop(f"nfe_temporaria_multiplo_{solicitacao_id}_pacote_{i}", None)
                    nota_fiscal = None

                    if dados_nfe:
                        nota_fiscal = NotaFiscal(
                            chave_acesso=dados_nfe.get("chave_acesso"),
                            arquivo_pdf=dados_nfe.get("arquivo_pdf"),
                            criado_por=session.get("usuario_id")
                        )
                        db.session.add(nota_fiscal)
                        db.session.flush()

                    pacote = PacoteEntrega(
                        compra_id=nova_compra.id,
                        quantidade=int(qtd) if qtd else 1,
                        senha_recebimento=senha,
                        data_prevista_entrega=data_entrega,
                        nota_fiscal_id=nota_fiscal.id if nota_fiscal else None,
                    )
                    db.session.add(pacote)

        solicitacao.status = "comprada"
        db.session.commit()

        flash(f"Dados de compra cadastrados para a Solicitação #{solicitacao.id}.", "success")
        return redirect(url_for("compras.lista_compras"))

    # GET: popular formulário com dados temporários de pacotes múltiplos
    session_notas = {}
    for key, value in session.items():
        if key.startswith(f"nfe_temporaria_multiplo_{solicitacao_id}_pacote_"):
            pacote_id = key.split("_pacote_")[1]
            session_notas[pacote_id] = {
                "chave_acesso": value.get("chave_acesso", ""),
                "arquivo_pdf": value.get("arquivo_pdf", "")
            }

    ultima_compra = (
        Compra.query
        .filter(Compra.item_id.in_([item.id for item in itens]))
        .order_by(Compra.id.desc())
        .first()
    )

    return render_template(
        "compras/detalhes.html",
        solicitacao=solicitacao,
        itens=itens,
        compra=ultima_compra,
        session_notas=session_notas
    )

# Preprocessar PDF e extrair chave
@compras_bp.route("/compras/nfe/preprocessar", methods=["POST"])
@login_required
@ativo_required
def preprocessar_nfe():
    file = request.files.get("arquivo")
    tipo = request.form.get("tipo") or "unico"
    pacote = request.form.get("pacote") or "0"
    solicitacao_id = request.form.get("solicitacao_id")

    if not file or not file.filename.endswith(".pdf"):
        flash("Arquivo inválido. Envie um PDF.", "danger")
        return redirect(request.referrer)

    filename = f"nfe_{uuid.uuid4().hex}.pdf"
    folder = os.path.join(current_app.static_folder, "uploads", "notas_temp")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)

    try:
        file.save(path)
        current_app.logger.info(f"[UPLOAD PREPROCESSAR] Arquivo salvo em: {path}")
    except Exception as e:
        current_app.logger.error(f"[ERRO AO SALVAR] {e}")
        flash("Erro ao salvar o arquivo.", "danger")
        return redirect(request.referrer)

    try:
        texto = extrair_texto_pdf_pypdf2(path)
        salvar_texto_temporario(texto)
        chave = extrair_chave_acesso(texto)
    except Exception as e:
        current_app.logger.error(f"[ERRO EXTRAÇÃO] {e}")
        chave = None

    blocos = chave.split() if chave else [""] * 11

    return render_template(
        "compras/nfe_confirma_chave.html",
        blocos=blocos,
        arquivo_pdf=filename,
        tipo=tipo,
        pacote=pacote,
        solicitacao_id=solicitacao_id
    )

@compras_bp.route("/compras/nfe/anexar/<tipo>/<int:solicitacao_id>", methods=["GET", "POST"])
@login_required
@ativo_required
def anexar_nfe(tipo, solicitacao_id):
    form = DummyForm()

    if tipo not in ("unico", "multiplo"):
        return abort(400, "Tipo inválido")

    if request.method == "POST":
        file = request.files.get("arquivo")
        if not file or not file.filename.endswith(".pdf"):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify(success=False, message="Envie um arquivo PDF válido."), 400
            flash("Envie um arquivo PDF válido.", "danger")
            return redirect(request.url)

        filename = f"nfe_{uuid.uuid4().hex}.pdf"
        upload_folder = os.path.join(current_app.static_folder, "uploads", "notas_temp")
        os.makedirs(upload_folder, exist_ok=True)
        path = os.path.join(upload_folder, filename)

        try:
            file.save(path)
        except Exception as e:
            msg = "Erro ao salvar arquivo: " + str(e)
            current_app.logger.exception(msg)
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify(success=False, message=msg), 500
            flash("Erro ao salvar o arquivo da nota fiscal.", "danger")
            return redirect(request.url)

        dados = extrair_dados_pdf(path)
        dados["arquivo_pdf"] = url_for("static", filename=f"uploads/notas_temp/{filename}")

        if tipo == "multiplo":
            pacote_id = request.args.get("pacote", type=int)
            if not pacote_id:
                return jsonify(success=False, message="Pacote não especificado"), 400

            session[f"nfe_temporaria_multiplo_{solicitacao_id}_pacote_{pacote_id}"] = dados

            return render_template(
                "compras/nfe_revisao.html",
                form=form,
                dados=dados,
                tipo=tipo,
                solicitacao_id=solicitacao_id,
                pacote=pacote_id
            )

        # tipo == unico
        session[f"nfe_temporaria_unico_{solicitacao_id}"] = dados

        flash("Nota Fiscal capturada com sucesso. Revise abaixo.", "success")
        return render_template(
            "compras/nfe_revisao.html",
            form=form,
            dados=dados,
            tipo=tipo,
            solicitacao_id=solicitacao_id,
            pacote=None
        )

    return render_template(
        "compras/nfe_upload.html",
        tipo=tipo,
        solicitacao_id=solicitacao_id,
        form=form
    )


# Confirmar Chave (POST)
@compras_bp.route("/compras/nfe/confirmar", methods=["POST"])
@login_required
@ativo_required
def confirmar_chave():
    blocos = [request.form.get(f"bloco{i}") for i in range(1, 12)]

    if not all(blocos) or any(len(b) != 4 for b in blocos):
        flash("Preencha os 11 blocos de 4 dígitos corretamente.", "danger")
        return redirect(request.referrer)

    chave_final = "".join(blocos)
    if len(chave_final) != 44 or not chave_final.isdigit():
        flash("Chave inválida. Corrija os blocos.", "danger")
        return redirect(request.referrer)

    tipo = request.form.get("tipo")
    solicitacao_id = request.form.get("solicitacao_id")
    pacote = request.form.get("pacote") or "0"

    chave_sessao = (
        f"nfe_temporaria_multiplo_{solicitacao_id}_pacote_{pacote}"
        if tipo == "multiplo"
        else f"nfe_temporaria_unico_{solicitacao_id}"
    )

    session[chave_sessao] = {
        "chave_acesso": chave_final,
        "pacote": pacote,
    }

    flash("Chave de acesso confirmada com sucesso.", "success")
    return redirect(url_for("compras.compra_detalhes", solicitacao_id=solicitacao_id))



# Proteção GET direto na rota POST
@compras_bp.route("/compras/nfe/confirmar_chave", methods=["GET"])
@login_required
@ativo_required
def confirmar_chave_get():
    flash("Acesso inválido. Use o formulário para confirmar a chave.", "warning")
    return redirect(url_for("compras.lista_compras"))

# Consulta API NFE.io
@compras_bp.route("/compras/nfe/consulta_api", methods=["POST"])
@login_required
@ativo_required
def consulta_api_nfe():
    chave = request.form.get("chave") or "".join(request.form.get(f"bloco{i}") for i in range(1, 12))

    if not chave.isdigit() or len(chave) != 44:
        flash("Chave inválida. Confirme os 11 blocos de 4 dígitos.", "danger")
        return redirect(request.referrer)

    try:
        dados_nota = consultar_nfe_nfeio(chave)
        return render_template("compras/nfe_dados_api.html", nota=dados_nota, chave=chave)
    except Exception as e:
        flash(f"Erro ao consultar a nota: {e}", "danger")
        return redirect(request.referrer)
