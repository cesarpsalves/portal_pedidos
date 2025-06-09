from datetime import datetime
from enum import IntEnum
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class Status(IntEnum):
    INATIVO = 0
    AGUARDANDO = 1
    ATIVO = 2

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id               = db.Column(db.Integer, primary_key=True)
    nome             = db.Column(db.String(120), nullable=False)
    email_principal  = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash       = db.Column(db.String(200), nullable=True)

    tipo             = db.Column(db.String(50), nullable=False, default="solicitante")
    perfis           = db.Column(db.String(300), nullable=False, default="solicitante")
    unidade_id       = db.Column(db.Integer, db.ForeignKey("unidades.id"), nullable=True)

    email_empresa    = db.Column(db.String(150), nullable=True)
    email_confirmado = db.Column(db.Boolean, default=False, nullable=False)

    google_id        = db.Column(db.String(200), unique=True, nullable=True)
    email_google     = db.Column(db.String(150), unique=True, nullable=True)

    logs = db.relationship("Log", back_populates="usuario")

    # ↓ substitui o antigo ativo
    status           = db.Column(db.SmallInteger,
                                 nullable=False,
                                 default=Status.AGUARDANDO)

    foto_url         = db.Column(db.String(500), nullable=True)
    criado_em        = db.Column(db.DateTime, default=datetime.utcnow)

    unidade = db.relationship("Unidade", back_populates="usuarios")

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)
