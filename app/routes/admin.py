# app/routes/admin.py

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request,
    flash,
)
from app.models.usuarios import Usuario
from app.models.unidades import Unidade
from app.extensions import db
from app.utils.auth import login_required

admin_bp = Blueprint("admin", __name__)

# Somente estes papéis podem acessar essa área:
PERFIS_GERENCIAIS = {"administrador", "gerente", "diretor"}

# Relação de todos os papéis possíveis
TODOS_OS_PERFIS = [
    "solicitante",
    "aprovador",
    "comprador",
    "recebedor",
    "tributario",
    "financeiro",
    "administrador",
    "gerente",
    "diretor",
]


@admin_bp.route("/admin/usuarios")
@login_required
def gerenciar_usuarios():
    tipo_usuario = session.get("usuario_tipo")

    # Somente administradores, gerentes, diretores, compradores ou aprovadores podem acessar
    if tipo_usuario not in PERFIS_GERENCIAIS.union({"comprador", "aprovador"}):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("main.dashboard"))

    usuarios = Usuario.query.order_by(Usuario.nome).all()
    unidades = Unidade.query.order_by(Unidade.nome).all()

    # --- 1) Monta “allowed_perfis” (papéis que o gestor logado pode atribuir) ---
    if tipo_usuario == "comprador":
        # Comprador pode atribuir “solicitante”, “aprovador”, “comprador”, “recebedor”
        allowed_perfis = ["solicitante", "aprovador", "comprador", "recebedor"]
    elif tipo_usuario == "aprovador":
        # Aprovador pode atribuir “solicitante”, “aprovador”, “recebedor”
        allowed_perfis = ["solicitante", "aprovador", "recebedor"]
    else:
        # Administrador, Gerente, Diretor podem ver/atribuir tudo
        allowed_perfis = TODOS_OS_PERFIS.copy()

    # --- 2) Monta “permitted_user_types” (quais usuários este gestor pode editar) ---
    if tipo_usuario == "comprador":
        permitted_user_types = {"solicitante", "aprovador", "comprador", "recebedor"}
    elif tipo_usuario == "aprovador":
        permitted_user_types = {"solicitante", "aprovador", "recebedor"}
    else:
        permitted_user_types = set(TODOS_OS_PERFIS)  # podem gerenciar qualquer tipo

    # Por fim, renderiza o template passando tudo que ele vai precisar:
    return render_template(
        "admin/usuarios.html",
        usuarios=usuarios,
        unidades=unidades,
        allowed_perfis=allowed_perfis,
        permitted_user_types=permitted_user_types,
        meu_tipo=tipo_usuario,
    )


@admin_bp.route("/admin/atualizar_perfis", methods=["POST"])
@login_required
def atualizar_perfis():
    tipo_usuario = session.get("usuario_tipo")

    # Restrição idêntica à de cima
    if tipo_usuario not in PERFIS_GERENCIAIS.union({"comprador", "aprovador"}):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("main.dashboard"))

    usuario_id = request.form.get("usuario_id")
    novos_perfis = request.form.getlist("perfis")
    nova_unidade_id = request.form.get("unidade_id")

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("admin.gerenciar_usuarios"))

    # --- 1) Reconstrói a lista “permitted” de perfis que o gestor logado pode atribuir ---
    if tipo_usuario == "comprador":
        permitted = {"solicitante", "aprovador", "comprador", "recebedor"}
    elif tipo_usuario == "aprovador":
        permitted = {"solicitante", "aprovador", "recebedor"}
    else:
        permitted = set(TODOS_OS_PERFIS)

    # Filtra para garantir que não haja perfil não permitido
    filtrados = [p for p in novos_perfis if p in permitted]
    usuario.perfis = ",".join(filtrados)

    # --- 2) Atualiza a unidade, apenas se foi passada alguma e se for válida ---
    if nova_unidade_id:
        try:
            uid = int(nova_unidade_id)
            unidade_obj = Unidade.query.get(uid)
            if unidade_obj:
                usuario.unidade_id = uid
            else:
                flash("Unidade selecionada inválida.", "warning")
        except ValueError:
            flash("Unidade inválida.", "warning")

    db.session.commit()
    flash(f"Dados de {usuario.nome} atualizados com sucesso.", "success")
    return redirect(url_for("admin.gerenciar_usuarios"))
