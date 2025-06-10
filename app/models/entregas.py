# app/models/entregas.py
from datetime import datetime
from app.extensions import db

class Entrega(db.Model):
    __tablename__ = "entregas"

    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey("compras.id"), nullable=False)
    nota_fiscal_id = db.Column(db.Integer, db.ForeignKey("notas_fiscais.id"), nullable=True)
    recebido_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    data_recebida = db.Column(db.Date)
    observacoes = db.Column(db.Text)

    nota_fiscal = db.relationship("NotaFiscal", backref="entregas")
    compra = db.relationship("Compra", backref="entrega")