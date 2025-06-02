from app.extensions import db


class EntregaRetirada(db.Model):
    __tablename__ = "entrega_retirada"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    tipo = db.Column(db.Enum("entrega", "retirada"), nullable=False)
    nome_recebedor = db.Column(db.String(100))
    cpf_recebedor = db.Column(db.String(20))
    telefone_recebedor = db.Column(db.String(20))
    endereco_entrega = db.Column(db.Text)
    unidade_retirada_id = db.Column(db.Integer, db.ForeignKey("unidades.id"))
