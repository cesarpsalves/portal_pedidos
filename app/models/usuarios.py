from app.extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(
        db.Enum(
            "solicitante",
            "aprovador",
            "comprador",
            "recebedor",
            "tributario",
            "financeiro",
            "administrador",
            "gerente",
            "diretor",
        ),
        nullable=False,
    )
    unidade_id = db.Column(db.Integer, db.ForeignKey("unidades.id"))
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, server_default=db.func.now())

    # ✅ Novo campo
    perfis = db.Column(db.String(255))
