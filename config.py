import os

env = os.environ.get("FLASK_ENV", "development")

if env == "production":
    from config_prod import ProdConfig as Config
else:
    from config_dev import DevConfig as Config
