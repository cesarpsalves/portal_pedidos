from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.extensions import db, mail
from app.models.usuarios import Usuario, Status
from app.models.unidades import Unidade
from app.utils.tokens import generate_confirmation_token, confirm_token
from flask_mail import Message
import os
import uuid
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
UPLOAD_FOLDER = os.path.join("app", "static", "uploads", "fotos")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/')
def view():
    user_id = session.get('usuario_id')
    if not user_id:
        flash('Faça login para acessar seu perfil.', 'warning')
        return redirect(url_for('auth.login'))
    user = Usuario.query.get(user_id)
    return render_template('profile/view.html', user=user)

@profile_bp.route('/edit', methods=['GET', 'POST'])
def edit():
    user_id = session.get('usuario_id')
    if not user_id:
        flash('Faça login para editar seu perfil.', 'warning')
        return redirect(url_for('auth.login'))
    user = Usuario.query.get(user_id)

    if request.method == 'POST':
        nome = request.form.get('nome', user.nome).strip()
        email_principal = request.form.get('email_principal', user.email_principal).strip().lower()
        email_empresa = request.form.get('email_empresa', user.email_empresa).strip().lower()
        arquivo_foto = request.files.get('foto')

        user.nome = nome
        user.email_empresa = email_empresa

        if email_principal != user.email_principal:
            if Usuario.query.filter_by(email_principal=email_principal).first():
                flash('E-mail de login já em uso.', 'danger')
                return redirect(url_for('profile.edit'))
            user.email_principal = email_principal
            dominio = "@" + email_principal.split("@")[1]
            dominios = current_app.config.get("DOMINIOS_AUTORIZADOS", [])
            user.status = Status.ATIVO if dominio in dominios else Status.AGUARDANDO
            user.email_confirmado = user.status == Status.ATIVO

        if arquivo_foto and allowed_file(arquivo_foto.filename):
            try:
                img = Image.open(arquivo_foto)
                img.thumbnail((400, 400))

                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)

                nome_arquivo = f"{uuid.uuid4().hex}.png"
                caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
                img.save(caminho_arquivo, optimize=True, quality=85)

                user.foto_url = url_for("static", filename=f"uploads/fotos/{nome_arquivo}")
                session["usuario_foto"] = user.foto_url

            except Exception as e:
                flash(f"Erro ao processar a imagem: {str(e)}", "danger")
                return redirect(url_for("profile.edit"))

        db.session.commit()
        flash('Perfil atualizado com sucesso.', 'success')
        return redirect(url_for('profile.view'))

    return render_template('profile/edit.html', user=user)

@profile_bp.route('/send-confirm')
def send_confirm():
    user_id = session.get('usuario_id')
    if not user_id:
        flash('Faça login para solicitar confirmação.', 'warning')
        return redirect(url_for('auth.login'))
    user = Usuario.query.get(user_id)
    if not user.email_empresa:
        flash('Informe seu e-mail da empresa antes.', 'warning')
        return redirect(url_for('profile.edit'))
    token = generate_confirmation_token(user.email_empresa)
    confirm_url = url_for('profile.confirm_email', token=token, _external=True)
    msg = Message('Confirme seu e-mail', recipients=[user.email_empresa])
    msg.body = f'Por favor, clique no link para confirmar seu e-mail: {confirm_url}'
    mail.send(msg)
    flash('E-mail de confirmação enviado. Verifique sua caixa de entrada.', 'info')
    return redirect(url_for('profile.view'))

@profile_bp.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    user = Usuario.query.filter_by(email_empresa=email).first()

    if not user or not email:
        flash('Link inválido ou expirado.', 'danger')
        return redirect(url_for('auth.login'))

    user.status = Status.ATIVO
    user.email_confirmado = True
    db.session.commit()
    flash('E-mail confirmado e conta ativada!', 'success')
    return redirect(url_for('main.dashboard'))

@profile_bp.route('/request-activation', methods=['GET', 'POST'])
def request_activation():
    if request.method == 'POST':
        email_login = request.form.get('email_principal', '').strip().lower()
        email_emp = request.form.get('email_empresa', '').strip().lower()
        unidade_id = request.form.get('unidade_id')

        if not email_login or not email_emp or not unidade_id:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('profile.request_activation'))

        user = Usuario.query.filter_by(email_principal=email_login).first()
        if not user or user.status != Status.AGUARDANDO:
            flash('Conta não encontrada ou não está pendente.', 'danger')
            return redirect(url_for('auth.login'))

        unidade = Unidade.query.get(int(unidade_id))
        if not unidade:
            flash('Unidade inválida.', 'danger')
            return redirect(url_for('profile.request_activation'))

        user.email_empresa = email_emp
        user.unidade_id = unidade.id
        db.session.commit()

        token = generate_confirmation_token(email_emp)
        confirm_url = url_for('profile.confirm_email', token=token, _external=True)

        sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        msg = Message(
            subject='Confirme seu e-mail para ativar conta',
            sender=sender,
            recipients=[email_emp]
        )
        msg.body = f'Clique no link para confirmar e ativar sua conta:\n\n{confirm_url}'
        mail.send(msg)

        flash('Pedido de ativação enviado. Verifique seu e-mail corporativo.', 'info')
        return redirect(url_for('auth.login'))

    unidades = Unidade.query.order_by(Unidade.nome).all()
    return render_template('profile/request_activation.html', unidades=unidades)
