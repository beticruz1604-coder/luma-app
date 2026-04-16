import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "nueve-lunas-dev-key-cambiar-en-produccion")
    # SQLite por defecto; para MySQL: mysql+pymysql://usuario:clave@localhost/nueve_lunas
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "nueve_lunas.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
