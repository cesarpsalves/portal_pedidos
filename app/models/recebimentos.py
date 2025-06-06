from app.extensions import db


class Recebimento(db.Model):
    __tablename__ = "recebimentos"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("itens_pedido.id"), nullable=False)
    recebido_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    status_recebimento = db.Column(
        db.Enum("recebido", "avaria", "recusado"), nullable=False
    )
    data_recebimento = db.Column(db.Date)
    observacoes = db.Column(db.Text)
