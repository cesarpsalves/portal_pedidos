from app.extensions import db


class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    nome_produto = db.Column(db.String(255), nullable=False)
    nome_tecnico = db.Column(db.String(255))
    especificacoes = db.Column(db.Text)
    quantidade = db.Column(db.String(50))
    unidade_medida = db.Column(db.String(50))
    tensao = db.Column(db.Enum("110/127V", "220V"))
    link_sugerido = db.Column(db.Text)
