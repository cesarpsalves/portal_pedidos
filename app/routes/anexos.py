import os
from flask import Blueprint, request, redirect, url_for, send_from_directory, flash
from app.extensions import db
from app.models.solicitacoes import AnexoSolicitacao
from app.models.solicitacoes import Solicitacao
from app.utils.auth import login_required
from flask import current_app as app

anexos_bp = Blueprint("anexos", __name__)


@anexos_bp.route("/download_anexo/<int:solicitacao_id>/<nome_arquivo>")
@login_required
def download_anexo(solicitacao_id, nome_arquivo):
    """
    Permite baixar um anexo já salvo.
    """
    pasta_base = app.config["UPLOAD_FOLDER"]
    caminho_solic = os.path.join(pasta_base, str(solicitacao_id))
    return send_from_directory(
        directory=caminho_solic,
        filename=nome_arquivo,
        as_attachment=True,
    )


@anexos_bp.route("/upload_anexo/<int:solicitacao_id>", methods=["POST"])
@login_required
def upload_anexo(solicitacao_id):
    """
    Recebe um arquivo via formulário, salva em disco e grava no banco.
    """
    solicitacao = Solicitacao.query.get_or_404(solicitacao_id)

    # Garante que a pasta exista (ex: uploads/solicitacoes/5/)
    pasta_base = app.config["UPLOAD_FOLDER"]
    pasta_solic = os.path.join(pasta_base, str(solicitacao_id))
    os.makedirs(pasta_solic, exist_ok=True)

    # Recupera o arquivo enviado pelo formulário (<input type="file" name="arquivo">)
    arquivo = request.files.get("arquivo")
    if not arquivo:
        flash("Nenhum arquivo selecionado.", "warning")
        return redirect(url_for("solicitacoes.ver_solicitacao", id=solicitacao_id))

    # Salva o arquivo na pasta dedicada: uploads/solicitacoes/<solicitacao_id>/
    nome_seguro = (
        arquivo.filename
    )  # você pode usar secure_filename(nome) se desejar sanitizar
    destino = os.path.join(pasta_solic, nome_seguro)
    arquivo.save(destino)

    # Insere registro de anexo na tabela 'anexos_solicitacao'
    novo_anexo = AnexoSolicitacao(
        solicitacao_id=solicitacao_id, nome_arquivo=nome_seguro, caminho_arquivo=destino
    )
    db.session.add(novo_anexo)
    db.session.commit()

    flash("Anexo enviado com sucesso!", "success")
    return redirect(url_for("solicitacoes.ver_solicitacao", id=solicitacao_id))
