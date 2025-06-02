from app.extensions import db


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    solicitante_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    unidade_id = db.Column(db.Integer, db.ForeignKey("unidades.id"), nullable=False)
    finalidade = db.Column(db.String(255))
    centro_custo = db.Column(db.String(50))
    tipo_entrega = db.Column(db.Enum("retirada", "entrega"), nullable=False)
    status = db.Column(
        db.Enum(
            "rascunho",
            "aguardando_aprovacao",
            "aprovado",
            "corrigir_itens",
            "em_compra",
            "recebendo",
            "recebido_parcial",
            "recebido_total",
            "divergencia_valor",
            "aguardando_nf",
            "cancelado",
            "concluido",
        ),
        default="rascunho",
    )
    prazo_limite = db.Column(db.Date)
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, server_default=db.func.now())
