from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy(
    session_options={"autocommit": False},
    engine_options={
        "pool_recycle": 280,
        "pool_pre_ping": True
    }
)
migrate = Migrate()

