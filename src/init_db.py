from src import create_app
from src.database import db

app = create_app()

with app.app_context():
    db.create_all()
    print("Database initialized!")