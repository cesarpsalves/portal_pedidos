from app.extensions import db


class HistoricoPedido(db.Model):
    __tablename__ = "historico_pedido"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    acao = db.Column(db.Text)
    data_acao = db.Column(db.DateTime, server_default=db.func.now())
