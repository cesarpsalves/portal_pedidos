from pytz import timezone
from datetime import datetime

def formatar_data_local(dt, formato="%d/%m/%Y %H:%M"):
    if not dt:
        return "---"
    fuso = timezone("America/Recife")  # ou "America/Sao_Paulo"
    return dt.astimezone(fuso).strftime(formato)

def registrar_filtros(app):
    app.jinja_env.filters["formatar_local"] = formatar_data_local
