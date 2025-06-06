# app/models/unidades.py

from app.extensions import db

class Unidade(db.Model):
    __tablename__ = "unidades"

    id       = db.Column(db.Integer, primary_key=True)
    nome     = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.Text)

    # RELACIONAMENTO COM Usuario:
    # • back_populates deve ser exatamente o mesmo nome usado em Usuario.unidade
    usuarios = db.relationship(
        "Usuario",            # nome da classe do outro lado do relacionamento
        back_populates="unidade",
        lazy="dynamic"        # opcional: define como você quer carregar a lista
    )
