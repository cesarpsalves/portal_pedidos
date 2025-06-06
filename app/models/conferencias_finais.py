from app.extensions import db


class ConferenciaFinal(db.Model):
    __tablename__ = "conferencias_finais"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    conferido_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    setor = db.Column(db.Enum("tributario", "financeiro"), nullable=False)
    valor_nf = db.Column(db.Numeric(10, 2))
    valor_pago = db.Column(db.Numeric(10, 2))
    divergencia = db.Column(db.Boolean)
    justificativa = db.Column(db.Text)
    concluido = db.Column(db.Boolean, default=False)
    data_conferencia = db.Column(db.DateTime, server_default=db.func.now())
