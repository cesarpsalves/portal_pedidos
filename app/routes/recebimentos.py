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
from app.models.solicitacoes import Solicitacao, AnexoSolicitacao, Entrega
from app.utils.auth import login_required

recebimentos_bp = Blueprint("recebimentos", __name__)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config.get(
        "ALLOWED_EXTENSIONS", {"pdf", "jpg", "jpeg", "png"}
    )

@recebimentos_bp.route("/recebimentos/anexar/<int:id>", methods=["GET", "POST"])
@login_required
def anexar_nota_fiscal(id):
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in ["recebedor", "administrador"]:
        flash("Acesso negado.", "danger")
        return redirect(url_for("main.dashboard"))

    solicitacao = Solicitacao.query.get_or_404(id)

    if solicitacao.status != "comprada":
        flash("Somente solicitações com status 'comprada' podem receber nota fiscal.", "warning")
        return redirect(url_for("recebimentos.lista_recebimentos"))

    if request.method == "POST":
        if "nota_fiscal" not in request.files:
            flash("Nenhum arquivo selecionado.", "danger")
            return redirect(request.url)

        file = request.files["nota_fiscal"]
        if file.filename == "":
            flash("Nenhum arquivo selecionado.", "warning")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            ext = file.filename.rsplit(".", 1)[1].lower()
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            filename = f"nota_fiscal_{solicitacao.id}_{timestamp}.{ext}"

            upload_base = app.config.get("UPLOAD_FOLDER", os.path.join("uploads", "notas_fiscais"))
            os.makedirs(upload_base, exist_ok=True)
            pasta_solic = os.path.join(upload_base, str(solicitacao.id))
            os.makedirs(pasta_solic, exist_ok=True)

            file_path = os.path.join(pasta_solic, filename)
            file.save(file_path)

            anexo = AnexoSolicitacao(
                solicitacao_id=solicitacao.id,
                nome_arquivo=filename,
                caminho_arquivo=file_path,
                criado_em=datetime.utcnow(),
            )
            db.session.add(anexo)

            solicitacao.status = "recebida"
            db.session.commit()

            flash("Nota fiscal anexada com sucesso.", "success")
            return redirect(url_for("recebimentos.lista_recebimentos"))
        else:
            flash("Formato de arquivo não permitido.", "warning")
            return redirect(request.url)

    return render_template("recebimentos/anexar_nota_fiscal.html", solicitacao=solicitacao)

@recebimentos_bp.route("/recebimentos")
@login_required
def lista_recebimentos():
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in ["recebedor", "administrador"]:
        flash("Acesso negado.", "danger")
        return redirect(url_for("main.dashboard"))

    solicitacoes = (
        Solicitacao.query.filter(Solicitacao.status == "comprada")
        .order_by(Solicitacao.criado_em.desc())
        .all()
    )

    return render_template("recebimentos/lista.html", solicitacoes=solicitacoes)

@recebimentos_bp.route("/recebimentos/confirmar/<int:id>", methods=["POST"])
@login_required
def confirmar_recebimento(id):
    tipo_usuario = session.get("usuario_tipo")
    if tipo_usuario not in ["recebedor", "administrador"]:
        flash("Acesso negado.", "danger")
        return redirect(url_for("main.dashboard"))

    solicitacao = Solicitacao.query.get_or_404(id)

    if solicitacao.status != "comprada":
        flash("Somente solicitações com status 'comprada' podem ser marcadas como recebidas.", "warning")
        return redirect(url_for("recebimentos.lista_recebimentos"))

    solicitacao.status = "recebida"
    solicitacao.recebido_em = datetime.utcnow()
    solicitacao.recebido_por = session.get("usuario_id")
    db.session.commit()

    flash(f"Solicitação #{id} marcada como recebida.", "success")
    return redirect(url_for("recebimentos.lista_recebimentos"))
