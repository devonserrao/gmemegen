from flask import (
    Flask, abort, request, redirect, url_for, render_template, g,
    send_from_directory, jsonify)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func

from configuration import (
    get_args, get_db_uri, get_templates_list,
    BASE_DIR, MEME_DIR, FONT_PATH)

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
db = SQLAlchemy(app)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Portfolio %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "owner": self.owner,
            "stocks_linked": [s.custom_serialize() for s in self.stocks_linked]
        }
