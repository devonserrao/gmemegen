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
