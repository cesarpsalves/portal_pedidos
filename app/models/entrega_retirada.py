# app/models/entrega_retirada.py
from datetime import datetime
from app.extensions import db

class EntregaRetirada(db.Model):
    __tablename__ = "entregas_retiradas"

    id = db.Column(db.Integer, primary_key=True)
    solicitacao_id = db.Column(db.Integer, db.ForeignKey("solicitacoes.id"), nullable=False)
    tipo = db.Column(db.Enum("entrega", "retirada"), nullable=False)
    nome_recebedor = db.Column(db.String(100))
    cpf_recebedor = db.Column(db.String(20))
    telefone_recebedor = db.Column(db.String(20))
    endereco_entrega = db.Column(db.Text)
    unidade_retirada_id = db.Column(db.Integer, db.ForeignKey("unidades.id"))
    data_agendada = db.Column(db.Date)
    data_confirmacao = db.Column(db.DateTime)

    solicitacao = db.relationship("Solicitacao", backref="entrega_retirada")
    unidade = db.relationship("Unidade", backref="entregas_retiradas")

    def __repr__(self):
        return f"<EntregaRetirada id={self.id} tipo={self.tipo}>"
