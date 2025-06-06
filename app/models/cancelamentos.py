from app.extensions import db


class Cancelamento(db.Model):
    __tablename__ = "cancelamentos"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    tipo_cancelamento = db.Column(
        db.Enum("usuario", "loja", "entrega", "avaria", "outros")
    )
    motivo = db.Column(db.Text)
    solicitado_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    aprovado_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    nf_cancelada = db.Column(db.Boolean, default=False)
    estorno_pendente = db.Column(db.Boolean, default=False)
    anexo_justificativa = db.Column(db.String(255))
    data_cancelamento = db.Column(db.DateTime, server_default=db.func.now())
