from dotenv import load_dotenv
load_dotenv()  # carrega as variáveis do .env

from flask_migrate import Migrate
from app import create_app
from app.extensions import db

app = create_app()
migrate = Migrate(app, db)

if __name__ == "__main__":
    # Em produção, você normalmente não roda diretamente com debug=True,
    # mas se quiser testar localmente, pode colocar debug=True.
    app.run(debug=True)
