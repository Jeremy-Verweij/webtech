import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from turbo_flask import Turbo
from flask_login import LoginManager

from utils.format_content import format_content, format_date

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
turbo = Turbo(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "database/db_alchemy_test.sqlite"
)

convention = {
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@app.context_processor
def custom_template_function():

    return dict(format_content=format_content, format_date=format_date)
