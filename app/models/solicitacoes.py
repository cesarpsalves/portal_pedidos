# app/models/solicitacoes.py

from datetime import datetime
from app.extensions import db


class Solicitacao(db.Model):
    __tablename__ = "solicitacoes"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    empresa_solicitante_id = db.Column(db.Integer, db.ForeignKey("empresas.id"))
    finalidade = db.Column(db.String(255), nullable=False)
    centro_custo = db.Column(db.String(255))  # novo campo
    unidade_id = db.Column(db.Integer, db.ForeignKey("unidades.id"), nullable=False)
    tipo_recebimento = db.Column(db.String(50), nullable=False)
    nome_retirada = db.Column(db.String(100))
    cpf_retirada = db.Column(db.String(15))
    prazo_limite = db.Column(db.Date)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="pendente")
    observacao = db.Column(db.Text)

    itens = db.relationship(
        "ItemSolicitacao",
        backref="solicitacao",
        lazy=True,
        cascade="all, delete-orphan",
    )
    anexos = db.relationship(
        "AnexoSolicitacao",
        backref="solicitacao",
        lazy=True,
        cascade="all, delete-orphan",
    )
    entregas = db.relationship(
        "Entrega", backref="solicitacao", lazy=True, cascade="all, delete-orphan"
    )

    usuario = db.relationship("Usuario", backref="solicitacoes", lazy=True)
    unidade = db.relationship("Unidade", backref="solicitacoes", lazy=True)
    empresa_solicitante = db.relationship("Empresa", backref="solicitacoes", lazy=True)

    def __repr__(self):
        return f"<Solicitacao {self.id} – {self.finalidade}>"


class ItemSolicitacao(db.Model):
    __tablename__ = "itens_solicitacao"

    id = db.Column(db.Integer, primary_key=True)
    solicitacao_id = db.Column(
        db.Integer, db.ForeignKey("solicitacoes.id"), nullable=False
    )
    nome_produto = db.Column(db.String(255), nullable=False)
    nome_tecnico = db.Column(db.String(255))
    quantidade = db.Column(db.Integer, default=1)
    voltagem = db.Column(db.String(10))
    especificacoes = db.Column(db.Text)
    link = db.Column(db.String(255))

    def __repr__(self):
        return f"<ItemSolicitacao {self.id} – {self.nome_produto}>"


# dentro de app/models/solicitacoes.py
class AnexoSolicitacao(db.Model):
    __tablename__ = "anexos_solicitacao"

    id = db.Column(db.Integer, primary_key=True)
    solicitacao_id = db.Column(
        db.Integer, db.ForeignKey("solicitacoes.id"), nullable=False
    )
    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho_arquivo = db.Column(db.String(255), nullable=False)
    enviado_em = db.Column(db.DateTime)  # << ESTE CAMPO ESTÁ AQUI?

    def __repr__(self):
        return f"<AnexoSolicitacao {self.id} – {self.nome_arquivo}>"


class Entrega(db.Model):
    __tablename__ = "entregas"

    id = db.Column(db.Integer, primary_key=True)
    solicitacao_id = db.Column(
        db.Integer, db.ForeignKey("solicitacoes.id"), nullable=False
    )
    data_entrega = db.Column(db.Date)
    qtde_pacote = db.Column(db.Integer, nullable=False, default=1)
    categoria = db.Column(db.String(50), default="único")
    nota_fiscal_anexada = db.Column(db.Boolean, default=False)
    senha_recebimento = db.Column(db.String(50))  # se houver
    observacoes = db.Column(db.Text)  # qualquer campo extra
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Entrega {self.id} para solicitacao {self.solicitacao_id}>"
