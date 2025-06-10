# app/models/notas_fiscais.py
from datetime import datetime
from app.extensions import db

class NotaFiscal(db.Model):
    __tablename__ = "notas_fiscais"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20))
    serie = db.Column(db.String(10))
    cnpj_emitente = db.Column(db.String(18))
    nome_emitente = db.Column(db.String(255))
    chave_acesso = db.Column(db.String(44), unique=True)
    data_emissao = db.Column(db.Date)
    valor_total = db.Column(db.Numeric(12, 2))
    valor_icms = db.Column(db.Numeric(12, 2))
    valor_ipi = db.Column(db.Numeric(12, 2))
    valor_frete = db.Column(db.Numeric(12, 2))
    arquivo_pdf = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    criado_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

    criado_por_usuario = db.relationship("Usuario", backref="notas_fiscais", lazy=True)