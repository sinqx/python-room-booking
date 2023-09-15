from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    """
    Создает и конфигурирует экземпляр Flask приложения.

    Returns:
        Flask приложение.
    """
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "SECRET_KEY"
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://postgres:password@localhost/postgres"
    db.init_app(app)

    # Импортируем и регистрируем синематические модули
    from .rooms import rooms
    from .auth import auth
    from .messages import messages

    app.register_blueprint(rooms, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(messages, url_prefix="/")

    # Импортируем модель пользователя
    from .models import User

    # Создаем все таблицы базы данных, если они еще не созданы
    with app.app_context():
        db.create_all()

    # Создаем экземпляр LoginManager и конфигурируем его
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        """
        Callback-функция для загрузки пользователя при входе в систему.

        Args:
            id (int): Идентификатор пользователя.

        Returns:
            Объект пользователя.
        """
        return User.query.get(int(id))

    return app


def create_database(app):
    """
    Создает базу данных, если она не существует.

    Args:
        app (Flask): Экземпляр Flask приложения.
    """
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Created Database!")
