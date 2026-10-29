from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app) -> None:
    db.init_app(app)
    with app.app_context():
        import models  # noqa: F401 (registreert de tabellen bij SQLAlchemy)

        db.create_all()
