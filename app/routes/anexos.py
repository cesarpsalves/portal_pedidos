# app/routes/anexos.py

import os
from flask import Blueprint, request, redirect, url_for, send_from_directory, flash, current_app as app
from app.extensions import db
from app.models.solicitacoes import AnexoSolicitacao, Solicitacao
from app.utils.auth import login_required, ativo_required
from werkzeug.utils import secure_filename

anexos_bp = Blueprint("anexos", __name__)


@anexos_bp.route("/download_anexo/<int:solicitacao_id>/<nome_arquivo>")
@login_required
@ativo_required
def download_anexo(solicitacao_id, nome_arquivo):
    """
    Permite baixar um anexo já salvo.
    """
    pasta_base = app.config["UPLOAD_FOLDER"]
    caminho_solic = os.path.join(pasta_base, str(solicitacao_id))
    return send_from_directory(
        directory=caminho_solic,
        path=nome_arquivo,
        as_attachment=True,
    )


@anexos_bp.route("/upload_anexo/<int:solicitacao_id>", methods=["POST"])
@login_required
@ativo_required
def upload_anexo(solicitacao_id):
    """
    Recebe um arquivo via formulário, salva em disco e grava no banco.
    """
    solicitacao = Solicitacao.query.get_or_404(solicitacao_id)

    pasta_base = app.config["UPLOAD_FOLDER"]
    pasta_solic = os.path.join(pasta_base, str(solicitacao_id))
    os.makedirs(pasta_solic, exist_ok=True)

    arquivo = request.files.get("arquivo")
    if not arquivo:
        flash("Nenhum arquivo selecionado.", "warning")
        return redirect(url_for("solicitacoes.ver_solicitacao", id=solicitacao_id))

    nome_seguro = secure_filename(arquivo.filename)
    destino = os.path.join(pasta_solic, nome_seguro)
    arquivo.save(destino)

    novo_anexo = AnexoSolicitacao(
        solicitacao_id=solicitacao_id,
        nome_arquivo=nome_seguro,
        caminho_arquivo=destino,
    )
    db.session.add(novo_anexo)
    db.session.commit()

    flash("Anexo enviado com sucesso!", "success")
    return redirect(url_for("solicitacoes.ver_solicitacao", id=solicitacao_id))
