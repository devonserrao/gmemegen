import os
import time
import json, urllib

from flask import (
    Flask, abort, request, redirect, url_for, render_template, g,
    send_from_directory, jsonify)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from PIL import Image, ImageDraw, ImageFont

# from packages.Stock import Stock
# from packages.Portfolio import Portfolio

from configuration import (
    get_args, get_db_uri, get_templates_list,
    BASE_DIR, MEME_DIR, FONT_PATH)

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
db = SQLAlchemy(app)

Portfolio_Stocks = db.Table(
    'Portfolio_Stocks',
    db.Column('stock_id', db.Integer, db.ForeignKey('stock.id'),
              primary_key=True),
    db.Column('portfolio_id', db.Integer, db.ForeignKey('portfolio.id'),
              primary_key=True)
)


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