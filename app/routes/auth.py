# app/routes/auth.py

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models.usuarios import Usuario
from app.models.unidades import Unidade

auth_bp = Blueprint("auth", __name__)

# -----------------------------
# Domínios permitidos (whitelist)
DOMINIOS_AUTORIZADOS = (
    "@kfp.com.br",
    "@kfp.net.br",
    "@grifcar.com.br",
)
# -----------------------------


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Login tradicional (e-mail + senha).
    - Se o usuário existir e a senha bater, verifica se 'ativo'
      ou, caso seja domínio interno, auto‐ativa. Caso contrário, bloqueia.
    - Armazena na sessão: usuario_id, usuario_nome, usuario_tipo, usuario_unidade_id.
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        # 1) Procura usuário pelo e-mail
        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            flash("E‐mail ou senha inválidos.", "danger")
            return redirect(url_for("auth.login"))

        # 2) Verifica a senha (caso usuário seja só Google, senha_hash pode ser None)
        if not usuario.senha_hash or not check_password_hash(usuario.senha_hash, senha):
            flash("E‐mail ou senha inválidos.", "danger")
            return redirect(url_for("auth.login"))

        # 3) Verifica se está ativo; se não estiver, mas for domínio interno, auto‐ativa
        dominio = "@" + email.split("@")[-1]
        if not usuario.ativo:
            if dominio in DOMINIOS_AUTORIZADOS:
                usuario.ativo = True
                db.session.commit()
                flash("Conta ativada automaticamente por domínio interno.", "info")
            else:
                flash("Sua conta ainda não foi ativada. Aguarde aprovação.", "warning")
                return redirect(url_for("auth.login"))

        # 4) Login bem‐sucedido: grava dados na sessão
        session["usuario_id"] = usuario.id
        session["usuario_nome"] = usuario.nome
        session["usuario_tipo"] = usuario.tipo
        session["usuario_unidade_id"] = usuario.unidade_id

        flash("Login realizado com sucesso!", "success")
        # ** ALTERAÇÃO IMPORTANTE **: redireciona para "main.dashboard" (não mais "exemplo.dashboard")
        return redirect(url_for("main.dashboard"))

    # GET: exibe o template de login (ajustado para procurar em 'templates/auth/')
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """
    Limpa a sessão e redireciona para a página de login.
    """
    session.clear()
    flash("Logout realizado com sucesso.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    """
    Cadastro manual de conta (e‐mail + senha + escolha de unidade).
    - Se e‐mail for de domínio interno, auto‐ativa (ativo=True).
    - Caso contrário, aguarda aprovação manual (ativo=False).
    - 'tipo' padrão: solicitante; 'perfis' inicial: "solicitante"
    """
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        unidade_id = request.form.get("unidade_id")

        # Validações
        if not nome or not email or not senha or not unidade_id:
            flash("Todos os campos são obrigatórios.", "danger")
            return redirect(url_for("auth.cadastro"))

        # Verifica email duplicado
        if Usuario.query.filter_by(email=email).first():
            flash("Este e‐mail já está cadastrado.", "warning")
            return redirect(url_for("auth.cadastro"))

        # Verifica unidade
        try:
            unidade_id_int = int(unidade_id)
            unidade_obj = Unidade.query.get(unidade_id_int)
            if not unidade_obj:
                raise ValueError
        except ValueError:
            flash("Unidade inválida. Escolha novamente.", "danger")
            return redirect(url_for("auth.cadastro"))

        # Auto‐ativa se for domínio interno
        dominio = "@" + email.split("@")[-1]
        is_ativo = dominio in DOMINIOS_AUTORIZADOS

        # Gera hash da senha
        from werkzeug.security import generate_password_hash

        hash_gerado = generate_password_hash(senha)

        # Cria o novo usuário
        novo = Usuario(
            nome=nome,
            email=email,
            senha_hash=hash_gerado,
            tipo="solicitante",
            unidade_id=unidade_obj.id,
            ativo=is_ativo,
            perfis="solicitante",
        )
        db.session.add(novo)
        db.session.commit()

        if is_ativo:
            flash("Cadastro realizado com sucesso! Você já pode fazer login.", "success")
        else:
            flash("Cadastro realizado! Aguarde aprovação de um usuário autorizado.", "info")

        return redirect(url_for("auth.login"))

    # GET: exibe o formulário de cadastro (template em 'templates/auth/')
    unidades = Unidade.query.order_by(Unidade.nome).all()
    return render_template("auth/cadastro.html", unidades=unidades)
