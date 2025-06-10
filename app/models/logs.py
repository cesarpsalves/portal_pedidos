from sqlalchemy import func
from app.extensions import db

class Log(db.Model):
    __tablename__ = 'logs'

    id           = db.Column(db.Integer, primary_key=True)
    usuario_id   = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    acao         = db.Column(db.String(255), nullable=False)
    descricao    = db.Column(db.String(500), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=func.now())

    # Relacionamento com Usuario (sem conflito)
    usuario      = db.relationship('Usuario', back_populates='logs')

    def __repr__(self):
        return f"<Log {self.acao} - {self.descricao}>"
