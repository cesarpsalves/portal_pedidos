# app/routes/recebimentos.py

import os
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app as app,
)
from app.extensions import db

# As três classes estão agora em app/models/solicitacoes.py:
from app.models.solicitacoes import Solicitacao, AnexoSolicitacao, Entrega

from app.utils.auth import login_required

recebimentos_bp = Blueprint("recebimentos", __name__)

# Caso ainda queira uma definição local, pode comentar/descomentar abaixo.
# Mas, em geral, armazenamos o caminho de upload em app.config para que fique centralizado.
# UPLOAD_FOLDER = os.path.join("uploads", "notas_fiscais")
# ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}


def allowed_file(filename):
    """
    Verifica se a extensão do arquivo está na lista de permitidas.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config.get(
        "ALLOWED_EXTENSIONS", {"pdf", "jpg", "jpeg", "png"}
    )


@recebimentos_bp.route("/recebimentos/anexar/<int:id>", methods=["GET", "POST"])
@login_required
def anexar_nota_fiscal(id):
    """
    Permite que o recebedor (ou administrador) anexe uma nota fiscal para uma solicitação
    que já esteja no status 'comprada'. Após anexar, a solicitação passa para status 'recebida'.
    """
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in ["recebedor", "administrador"]:
        flash("Acesso negado.", "danger")
        return redirect(url_for("main.dashboard"))

    solicitacao = Solicitacao.query.get_or_404(id)

    # Somente solicitações com status 'comprada' podem ter NF anexada
    if solicitacao.status != "comprada":
        flash(
            "Somente solicitações com status 'comprada' podem receber nota fiscal.",
            "warning",
        )
        return redirect(url_for("recebimentos.lista_recebimentos"))

    if request.method == "POST":
        # Verifica se veio o campo 'nota_fiscal' no form
        if "nota_fiscal" not in request.files:
            flash("Nenhum arquivo selecionado.", "danger")
            return redirect(request.url)

        file = request.files["nota_fiscal"]
        if file.filename == "":
            flash("Nenhum arquivo selecionado.", "warning")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Gera nome único para o arquivo
            ext = file.filename.rsplit(".", 1)[1].lower()
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            filename = f"nota_fiscal_{solicitacao.id}_{timestamp}.{ext}"

            # Usa o diretório configurado em app.config["UPLOAD_FOLDER"]
            upload_base = app.config.get(
                "UPLOAD_FOLDER", os.path.join("uploads", "notas_fiscais")
            )
            os.makedirs(upload_base, exist_ok=True)

            # Para manter as NFs organizadas por solicitação, guardamos numa subpasta:
            pasta_solic = os.path.join(upload_base, str(solicitacao.id))
            os.makedirs(pasta_solic, exist_ok=True)

            file_path = os.path.join(pasta_solic, filename)
            file.save(file_path)

            # Cria o registro de AnexoSolicitacao
            anexo = AnexoSolicitacao(
                solicitacao_id=solicitacao.id,
                nome_arquivo=filename,
                caminho_arquivo=file_path,
                criado_em=datetime.utcnow(),
            )
            db.session.add(anexo)

            # Atualiza status da solicitação para 'recebida'
            solicitacao.status = "recebida"
            db.session.commit()

            flash("Nota fiscal anexada com sucesso.", "success")
            return redirect(url_for("recebimentos.lista_recebimentos"))
        else:
            flash("Formato de arquivo não permitido.", "warning")
            return redirect(request.url)

    # Se GET, renderiza o formulário de upload de nota
    return render_template(
        "recebimentos/anexar_nota_fiscal.html", solicitacao=solicitacao
    )


@recebimentos_bp.route("/recebimentos")
@login_required
def lista_recebimentos():
    """
    Exibe todas as solicitações com status 'comprada',
    para que o recebedor possa anexar nota fiscal e confirmar recebimento.
    """
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in ["recebedor", "administrador"]:
        flash("Acesso negado.", "danger")
        return redirect(url_for("main.dashboard"))

    # Puxamos as solicitações cujo status seja exatamente 'comprada'
    solicitacoes = (
        Solicitacao.query.filter(Solicitacao.status == "comprada")
        .order_by(Solicitacao.criado_em.desc())
        .all()
    )

    return render_template("recebimentos/lista.html", solicitacoes=solicitacoes)


@recebimentos_bp.route("/recebimentos/confirmar/<int:id>", methods=["POST"])
@login_required
def confirmar_recebimento(id):
    """
    Após anexar nota fiscal ou verificar NF, o recebedor marca 'confirmar recebimento'.
    Isso muda o status para 'recebida' e armazena quem e quando recebeu.
    """
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in ["recebedor", "administrador"]:
        flash("Acesso negado.", "danger")
        return redirect(url_for("main.dashboard"))

    solicitacao = Solicitacao.query.get_or_404(id)

    if solicitacao.status != "comprada":
        flash(
            "Somente solicitações com status 'comprada' podem ser marcadas como recebidas.",
            "warning",
        )
        return redirect(url_for("recebimentos.lista_recebimentos"))

    # Atualiza campos de recebimento
    solicitacao.status = "recebida"
    solicitacao.recebido_em = datetime.utcnow()
    solicitacao.recebido_por = session.get("usuario_id")
    db.session.commit()

    flash(f"Solicitação #{id} marcada como recebida.", "success")
    return redirect(url_for("recebimentos.lista_recebimentos"))