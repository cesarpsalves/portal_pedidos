# app/models/empresas.py

from datetime import datetime
from app.extensions import db


class Empresa(db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False, unique=True)
    tipo = db.Column(
        db.Enum("juridica", "fisica", name="tipo_empresa"),
        nullable=False,
        default="juridica",
    )
    documento = db.Column(db.String(20), nullable=True)  # CNPJ ou CPF, a seu critério
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Empresa {self.nome}>"


# ========================================================
# Pequeno “seed” para criar algumas empresas de teste.
# Basta executar este bloco em um shell Python dentro do seu venv:
#
#    >>> from app.extensions import db
#    >>> from app import create_app
#    >>> app = create_app()
#    >>> ctx = app.app_context(); ctx.push()
#    >>> from app.models.empresas import Empresa
#    >>> # Apaga tudo (cuidado: apenas se quiser resetar!)
#    >>> # Empresa.query.delete(); db.session.commit()
#    >>> #
#    >>> e1 = Empresa(nome="ACME Indústria e Comércio Ltda", tipo="juridica", documento="12.345.678/0001-90")
#    >>> e2 = Empresa(nome="Beta Serviços ME", tipo="juridica", documento="98.765.432/0001-10")
#    >>> e3 = Empresa(nome="José da Silva (PF)", tipo="fisica", documento="123.456.789-00")
#    >>> db.session.add_all([e1, e2, e3])
#    >>> db.session.commit()
#
# Após isso, você terá três registros em `empresas`:
#  - ACME Indústria e Comércio Ltda (jurídica, CNPJ fictício)
#  - Beta Serviços ME (jurídica, CNPJ fictício)
#  - José da Silva (pessoa física, CPF fictício)
#
# Você pode executar o seed quantas vezes quiser, ajustando conforme necessário.
# ========================================================
