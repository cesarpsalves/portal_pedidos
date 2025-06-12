# app/routes/nfe.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.auth import login_required, ativo_required
from app.utils.nfe_utils import extrair_dados_pdf
import os
import uuid

nfe_bp = Blueprint("nfe", __name__)

@nfe_bp.route("/compras/nfe/upload", methods=["GET", "POST"])
@login_required
@ativo_required
def upload_nfe():
    index = request.args.get("index", default=0, type=int)

    if request.method == "POST":
        file = request.files.get("arquivo")
        if not file or not file.filename.endswith(".pdf"):
            flash("Arquivo inválido. Envie um PDF.", "danger")
            return redirect(request.url)

        filename = f"nfe_{uuid.uuid4().hex}.pdf"
        folder = os.path.join("static", "uploads", "notas_temp")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
        file.save(path)

        dados_extraidos = extrair_dados_pdf(path)
        dados_extraidos["arquivo_pdf"] = path.replace("static", "")
        session.setdefault("notas_temp", {})
        session["notas_temp"][str(index)] = dados_extraidos
        session.modified = True

        return render_template("compras/nfe_revisao.html", dados=dados_extraidos, index=index)

    return render_template("compras/nfe_upload.html", index=index)
