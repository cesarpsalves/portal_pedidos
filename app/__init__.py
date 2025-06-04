# app/__init__.py

import os
from flask import Flask, current_app
from flask_wtf import CSRFProtect
from app.extensions import db, migrate
from datetime import datetime

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    @app.context_processor
    def inject_ano():
        return {"ano": datetime.now().year}

    # ── NOVO ── Expor current_app ao contexto de templates ──
    @app.context_processor
    def expose_current_app():
        return {"current_app": current_app}
    # ────────────────────────────────────────────────────────

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.solicitacoes import solicitacoes_bp
    from app.routes.anexos import anexos_bp
    from app.routes.admin import admin_bp
    from app.routes.aprovacoes import aprovacoes_bp
    from app.routes.compras import compras_bp
    from app.routes.historico import historico_bp
    from app.routes.recebimentos import recebimentos_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(solicitacoes_bp)
    app.register_blueprint(anexos_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(aprovacoes_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(historico_bp)
    app.register_blueprint(recebimentos_bp)

    return app
