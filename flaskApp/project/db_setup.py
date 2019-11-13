import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# db config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Listing(db.Model):

    __tablename__ = 'Listings'
    id = db.Column(db.Integer, primary_key=True)
    centris_id = db.Column(db.Integer)
    category = db.Column(db.Text)
    price = db.Column(db.Integer)
    centris_detail_url = db.Column(db.Text)
    broker_detail_url = db.Column(db.Text)
    lat = db.Column(db.Text)
    lng = db.Column(db.Text)

    def __init__(self, centris_id, category, price, centris_detail_url,
                 broker_detail_url, lat, lng):
        self.centris_id = centris_id
        self.category = category
        self.price = price
        self.centris_detail_url = centris_detail_url
        self.broker_detail_url = broker_detail_url
        self.lat = lat
        self.lng = lng

    def __repr__(self):
        return f"{self.category} at {self.price}$ id #{self.centris_id}"
