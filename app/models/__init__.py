# app/models/__init__.py

from .usuarios import Usuario
from .unidades import Unidade
from .empresas import Empresa

# As classes que estavam antes espalhadas em arquivos separados:
from .solicitacoes import Solicitacao, ItemSolicitacao, AnexoSolicitacao, Entrega

# Outros modelos (compras, recebimentos etc.):
from .compras import Compra
from .recebimentos import Recebimento

# ... importe outros modelos conforme seu projeto ...
