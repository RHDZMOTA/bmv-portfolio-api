from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('app_config')

db = SQLAlchemy(app)


from app.mod_sharpe.controller import mod_sharpe as sharpe
app.register_blueprint(sharpe)

from app.mod_markowitz.controller import mod_markowitz as markowitz
app.register_blueprint(markowitz)


db.create_all()