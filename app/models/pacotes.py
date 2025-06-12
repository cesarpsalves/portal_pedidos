# app/models/pacotes.py

from datetime import datetime
from app.extensions import db
from app.models.notas_fiscais import NotaFiscal  # usa o model oficial

class PacoteEntrega(db.Model):
    __tablename__ = "pacote_entrega"

    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey("compras.id"), nullable=False)
    senha_recebimento = db.Column(db.String(100))
    data_prevista = db.Column(db.Date, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    notas_fiscais = db.relationship("NotaFiscal", backref="pacote", lazy=True)
