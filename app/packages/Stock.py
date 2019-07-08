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

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    portfolios_linked = db.relationship('Portfolio',
                                        secondary=Portfolio_Stocks,
                                        lazy='subquery',
                                        backref=db.backref('stocks_linked',
                                                           lazy=True)
                                        )

    def __repr__(self):
        return '<Stock %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "price": self.price,
            "portfolios_linked": [p.owner for p in self.portfolios_linked]
        }
    
    def custom_serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "price": self.price
        }