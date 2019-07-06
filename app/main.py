# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
import json, urllib

from flask import (
    Flask, abort, request, redirect, url_for, render_template, g,
    send_from_directory, jsonify)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from PIL import Image, ImageDraw, ImageFont

from configuration import (
    get_args, get_db_uri, get_templates_list,
    BASE_DIR, MEME_DIR, FONT_PATH)

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
db = SQLAlchemy(app)


# Model for representing created Memes
class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template = db.Column(db.String(80), nullable=False)
    top_text = db.Column(db.String(80), nullable=False)
    bot_text = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Meme %r>' % self.id


Portfolio_Stocks = db.Table(
    'Portfolio_Stocks',
    db.Column('stock_id', db.Integer, db.ForeignKey('stock.id'),
              primary_key=True),
    db.Column('portfolio_id', db.Integer, db.ForeignKey('portfolio.id'),
              primary_key=True)
)


# class Stock(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), nullable=False)
#     symbol = db.Column(db.String(10), nullable=False)
#     price = db.Column(db.Float, nullable=False)

#     def __repr__(self):
#         return '<Stock %r>' % self.id


# class Portfolio(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     portfolio_owner = db.Column(db.String(80), nullable=False)
#     stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=Fals
#     e)

#     def __repr__(self):
#         return '<Portfolio %r>' % self.id
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
            "price": self.price
        }


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Portfolio %r>' % self.id


# Portfolio_Stocks = db.Table(
#     db.Column('stock_id', db.Integer, db.ForeignKey('stock.id'),
#               primary_key=True),
#     db.Column('portfolio_id', db.Integer, db.ForeignKey('portfolio.id'),
#               primary_key=True)
# )
#
#
@app.before_first_request
def setup_db():
    # Create folder for memes if it doesn't exist
    if not os.path.exists(MEME_DIR):
        os.makedirs(MEME_DIR)
    # Create tables for models if they don't exist
    db.create_all()


@app.before_request
def setup_request_time():
    start_time = time.time()
    g.request_time = lambda: "%d ms" % ((time.time() - start_time) * 1000)


@app.route('/')
def index():
    return redirect(url_for("get_create_menu"))


@app.route('/recent', methods=['GET'])
def view_recent():
    memes = Meme.query.order_by(Meme.id.desc()).limit(20).all()
    return render_template('recent.html', memes=memes)


@app.route('/random', methods=['GET'])
def view_random():
    meme = Meme.query.order_by(func.random()).first()
    return redirect(url_for('view_meme', meme_id=meme.id))


@app.route('/template', methods=['GET'])
def get_create_menu():
    templates = get_templates_list()
    return render_template('view.html', templates=templates)


@app.route('/template/<string:template>', methods=['GET'])
def get_create(template):
    if template not in get_templates_list():
        abort(400, "Template does not exist.")
    return render_template('create_meme.html', template=template)


@app.route('/meme/<int:meme_id>', methods=['GET'])
def view_meme(meme_id):
    meme_file = os.path.join(MEME_DIR, '%d.png' % meme_id)
    if not os.path.exists(meme_file):
        generate_meme(meme_file, meme_id)
    print(meme_file)
    return send_from_directory(MEME_DIR, '%d.png' % meme_id)


@app.route('/meme', methods=['POST'])
def create_meme():
    try:
        meme = Meme(
            template=request.form['template'],
            top_text=request.form['top'],
            bot_text=request.form['bottom']
        )
        db.session.add(meme)
        db.session.commit()

        return redirect(url_for('view_meme', meme_id=meme.id))
    except KeyError:
        abort(400, "Incorrect parameters.")


# Creates a stock
@app.route('/stock', methods=["POST"])
def create_stock():
    try:
        stock = Stock(
            name=request.form['name'],
            symbol=request.form['symbol'],
            price=request.form['price']
            )
        db.session.add(stock)
        db.session.commit()

        print("stock created!")
        # return redirect(url_for('view_stock', stock_id=stock.id))
        return redirect('/template')
    except KeyError:
        abort(400, "Incorrect Parameters!")


############################################## NOT YET COMPLETE ##################################################
# Creates a stock to api
@app.route('/ap1/v1/stocks', methods=["POST"])
def api_create_stock():
    try:
       # stock = Stock(
       #         name=request.form['name'],
       #         symbol=request.form['symbol'],
       #         price=request.form['price']
       #        )
       # stock.serialize(
        data=request.data
        dataDict=json.loads(data)
        stock = Stock(name=dataDict['name'],symbol=dataDict['symbol'],price=dataDict['price'])

        db.session.add(stock)
        db.session.commit()
        print("stock created through API")
    except KeyError:
        abort(400,"Parameters Incorrect!")
#####################################################################################################################


# Helper method to get all stocks from database 
def helper_get_stocks_from_db():
    stocks = Stock.query.order_by(Stock.id.desc()).all()
    return stocks


# Helper function to get all stocks from database with a certain NAME
def helper_get_stocks_with_name_from_db(filterName):
    stocks = Stock.query.filter_by(name=filterName).all()
    return stocks


# Gets all stocks from api
@app.route('/api/v1/stocks', methods=["GET"])
def api_stocks():
    ###args = dict(request.args)
    # filterName = request.args.get("name")
    # stocks = Stock.query.filter_by(name=filterName).all()
    # if filterName is None:
    #     stocks = Stock.query.order_by(Stock.id.desc()).all()
    # return jsonify([s.serialize() for s in stocks])
    filterName = request.args.get("name")
    stocks = helper_get_stocks_from_db()
    if filterName is not None:
        stocks = helper_get_stocks_with_name_from_db(filterName)
    return jsonify([s.serialize() for s in stocks])

# Gets all stocks
@app.route('/stock', methods=["GET"])
def view_stocks():
    # print(api_stocks().json())
    # data = json.loads(api_stocks()) ### CONTINUE FROM HERE#######################################
    # # data = json.loads(json_url.read())
    # print(data)
    # stocks = Stock.query.order_by(Stock.id.desc()).all()
    # return render_template('stocks.html', stocks=stocks)
    stocks = helper_get_stocks_from_db()
    return render_template('stocks.html', stocks=stocks)


# Gets stock from api by stock id
@app.route('/api/v1/stocks/<int:stock_id>', methods=["GET"])
def api_stock_by_id(stock_id):
    stock = Stock.query.filter_by(id=stock_id).first()
    return jsonify(stock.serialize())


# Gets stock from api by stock name
@app.route('/api/v1/stocks?name=<string:stock_name>', methods=["GET"])
def api_stock_by_name(stock_name):
    stock = Stock.query.filter_by(name=stock_name).first()
    return jsonify(stock.serialize())
    

# Gets stock from api by stock symbol
@app.route('/api/v1/stocks?symbol=<string:stock_symbol>', methods=["GET"])
def api_stock_by_symbol(stock_symbol):
    stock = Stock.query.filter_by(symbol=stock_symbol).first()
    return jsonify(stock.serialize())

# Get stock by stock id
@app.route('/stock/<int:stock_id>', methods=["GET"])
def view_stock(stock_id):
    stock = Stock.query.filter_by(id=stock_id).first()
    return render_template('stock_id.html', stock=stock)


# Renders create_stock.html
@app.route('/stock/cstock', methods=["GET"])
def get_create_stock():
    return render_template("create_stock.html")


# Renders create_stock.html
@app.route('/portfolio/cportfolio', methods=["GET"])
def get_create_portfolio():
    return render_template("create_portfolio.html")


# Creates a portfolio
@app.route('/portfolio', methods=["POST"])
def create_portfolio():
    try:
        portfolio = Portfolio(
            owner=request.form['owner']
        )
        db.session.add(portfolio)
        db.session.commit()

        print("portfolio created!")
        return redirect('/template')
    except KeyError:
        abort(400, "Incorrect Parameters!")


# Gets all portfolios
@app.route('/portfolio', methods=["GET"])
def view_portfolios():
    portfolios = Portfolio.query.order_by(Portfolio.id.desc()).all()
    return render_template('portfolios.html', portfolios=portfolios)


# Gets portfolio by stock id
@app.route('/portfolio/<int:portfolio_id>', methods=["GET"])
def view_portfolio(portfolio_id):
    portfolio = Portfolio.query.filter_by(id=portfolio_id).first()
    return render_template('portfolio_id.html', portfolio=portfolio)


# Allows a stock to be assigned to a portfolio
@app.route('/portfolio/psip', methods=["POST"])
def put_stock_in_portfolio(stock_id, portfolio_id):
    portfolio_rel = Portfolio.query.filter_by(id=portfolio_id).first()
    stock_rel = Stock.query.filter_by(id=stock_id).first()

    portfolio_rel.stocks_linked.append(stock_rel)
    print("stock assigned to portfolio")
    db.session.commit()
    # return redirect('/template')
    return render_template('portfolio_id.html', portfolio=portfolio_rel)


def generate_meme(file, meme_id):
    # Query for meme
    meme = Meme.query.filter(Meme.id == meme_id).first()
    if meme is None:
        abort(400, 'Meme does not exist.')
    # Load template
    template_file = os.path.join(
        BASE_DIR, 'static', 'templates', meme.template)
    if not os.path.exists(template_file):
        abort(400, 'Template does not exist')
    template = Image.open(template_file)
    # Get Font Details
    font, top_loc, bot_loc = calc_font_details(
        meme.top_text, meme.bot_text, template.size)
    draw = ImageDraw.Draw(template)
    draw_text(draw, top_loc[0], top_loc[1], meme.top_text, font)
    draw_text(draw, bot_loc[0], bot_loc[1], meme.bot_text, font)

    template.save(file)


# Calculate font size and location
def calc_font_details(top, bot, img_size):
    font_size = 50
    font = ImageFont.truetype(FONT_PATH, font_size)
    max_width = img_size[0] - 20
    # Get ideal font size
    while font.getsize(top)[0] > max_width or font.getsize(bot)[0] > max_width:
        font_size = font_size - 1
        font = ImageFont.truetype(FONT_PATH, font_size)
    # Get font locations
    top_loc = ((img_size[0] - font.getsize(top)[0])/2, -5)
    bot_size = font.getsize(bot)
    bot_loc = ((img_size[0] - bot_size[0])/2, img_size[1] - bot_size[1] - 5)
    return font, top_loc, bot_loc


# Draws the given text with a border
def draw_text(draw, x, y, text, font):
    # Draw border
    draw.text((x-1, y-1), text, font=font, fill="black")
    draw.text((x+1, y-1), text, font=font, fill="black")
    draw.text((x-1, y+1), text, font=font, fill="black")
    draw.text((x+1, y+1), text, font=font, fill="black")
    # Draw text
    draw.text((x, y), text, font=font, fill="white")


if __name__ == '__main__':
    # Run dev server (for debugging only)
    args = get_args()
    app.run(host=args.host, port=args.port, debug=True)
