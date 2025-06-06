# app/models/usuarios.py

from datetime import datetime
from app.extensions import db

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=True)  # nullable=True porque login Google não precisa de senha
    tipo = db.Column(db.String(50), nullable=False, default="solicitante")
    unidade_id = db.Column(db.Integer, db.ForeignKey("unidades.id"), nullable=True)
    ativo = db.Column(db.Boolean, default=False, nullable=False)
    google_id = db.Column(db.String(200), unique=True, nullable=True)
    foto_url = db.Column(db.String(500), nullable=True)
    email_confirmado = db.Column(db.Boolean, default=False, nullable=False)
    perfis = db.Column(db.String(300), nullable=False, default="solicitante")
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    unidade = db.relationship("Unidade", back_populates="usuarios")
