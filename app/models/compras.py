# app/models/compras.py

from datetime import datetime
from app.extensions import db


class Compra(db.Model):
    __tablename__ = "compras"

    id = db.Column(db.Integer, primary_key=True)

    # Referência ao item solicitado (cada linha de Compra ↔ 1 ItemSolicitacao)
    item_id = db.Column(
        db.Integer, db.ForeignKey("itens_solicitacao.id"), nullable=False
    )

    # Usuário que efetuou a compra (comprador)
    comprado_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    # Valor efetivamente pago (pode divergir de valor_total se houver acréscimos/descontos adicionais)
    valor_pago = db.Column(db.Numeric(10, 2))

    # Dados de pagamento
    forma_pagamento = db.Column(
        db.String(100)
    )  # Ex: "Cartão de Crédito", "Boleto", "PIX" etc.
    cartao_ultimos_digitos = db.Column(
        db.String(4)
    )  # Se for cartão de crédito, últimos 4 dígitos

    # Valor total da compra para este item
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)

    # Caso seja parcelado, número de parcelas
    parcelamento = db.Column(db.Integer)

    # Valor de desconto aplicado
    desconto = db.Column(db.Numeric(10, 2), default=0)

    # Informações adicionais (rastreio, observações, divisão de pacotes etc.)
    informacoes_adicionais = db.Column(db.Text)

    # Senha de recebimento (cada item/pacote pode ter senha separada)
    senha_recebimento = db.Column(db.String(50))

    # Dados da loja onde foi comprada
    loja_nome = db.Column(
        db.String(255)
    )  # Nome da loja/plataforma (Mercado Livre, Amazon etc.)
    loja_inscricao_estadual = db.Column(
        db.String(20)
    )  # Inscrição Estadual da loja (opcional)

    # Categoria de entrega: único pacote ou múltiplos pacotes
    entrega_categoria = db.Column(
        db.String(20), default="único"
    )  # "único" ou "múltiplos"

    # Data prevista para entrega (caso informada no momento da compra)
    data_prevista_entrega = db.Column(db.Date)

    # Data em que a compra foi registrada no sistema
    data_compra = db.Column(db.DateTime, default=datetime.utcnow)

    # ---- Relacionamentos ----

    # Relaciona Compra → ItemSolicitacao (cada Compra refere-se a um item específico)
    item = db.relationship("ItemSolicitacao", backref="compras", lazy=True)

    # Relaciona Compra → Usuário (quem efetuou a compra)
    usuario = db.relationship("Usuario", backref="compras", lazy=True)

    def __repr__(self):
        return f"<Compra id={self.id} item_id={self.item_id} valor_total={self.valor_total}>"
