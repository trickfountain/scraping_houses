from app import db


class Listing(db.Model):

    __tablename__ = 'Listings'
    id = db.Column(db.Integer, primary_key=True)
    centris_id = db.Column(db.Integer)
    category = db.Column(db.Text)
    title = db.Column(db.Text)
    price = db.Column(db.Integer)
    city = db.Column(db.Text)
    centris_detail_url = db.Column(db.Text)
    broker_detail_url = db.Column(db.Text)
    lat = db.Column(db.Text)
    lng = db.Column(db.Text)
    address = db.Column(db.Text)
    postal_code = db.Column(db.Text)
    description = db.Column(db.Text)
    potential_revenue = db.Column(db.Integer)
    features = db.Column(db.Text)
    first_seen = db.Column(db.Text)
    last_seen = db.Column(db.Text)

    def __init__(self, listing_number, centris_id, category, title, price, city, centris_detail_url,
                 broker_detail_url, lat, lng, address, postal_code, description, potential_revenue, features,
                 first_seen, last_seen):
        self.centris_id = centris_id
        self.category = category
        self.title = title
        self.price = price
        self.city = city
        self.centris_detail_url = centris_detail_url
        self.broker_detail_url = broker_detail_url
        self.lat = lat
        self.lng = lng
        self.address = address
        self.postal_code = postal_code
        self.description = description
        self.potential_revenue = potential_revenue
        self.features = features
        self.first_seen = first_seen
        self.last_seen = last_seen

    def __repr__(self):
        return f"{self.category} at {self.price}$ id #{self.centris_id}"
