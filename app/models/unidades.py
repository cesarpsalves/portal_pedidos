from app.extensions import db


class Unidade(db.Model):
    __tablename__ = "unidades"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.Text)
