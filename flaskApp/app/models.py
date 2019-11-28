from app import db
import json


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
    residential_units = db.Column(db.Text)
    commercial_units = db.Column(db.Text)
    unites_residentielles = db.Column(db.Text)
    unite_principale = db.Column(db.Text)
    features = db.Column(db.Text)
    first_seen = db.Column(db.Text)
    last_seen = db.Column(db.Text)
    geofence = db.Column(db.Text)

    def __init__(self, listing_number, centris_id, category, title, price, city, centris_detail_url,
                 broker_detail_url, lat, lng, address, postal_code, description, potential_revenue, features,
                 residential_units, commercial_units, unites_residentielles, unite_principale, first_seen, last_seen, geofence):
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
        self.residential_units = residential_units
        self.commercial_units = commercial_units
        self.unites_residentielles = unites_residentielles
        self.unite_principale = unite_principale
        self.features = features
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.geofence = geofence

    def __repr__(self):
        return f"{self.category} at {self.price}$ id #{self.centris_id}"


class Fence(db.Model):
    """Table containing geofences.
    Used to filter querries on the front end.
    coords should be loaded as a list of lat,lng tuples.
    To accomodate SQLite it's transformed to a json string for now.
    """

    __tablename__ = 'Fences'
    id = db.Column(db.Integer, primary_key=True)
    area_name = db.Column(db.Text)
    coords = db.Column(db.Text)

    def __init__(self, area_name, coords):
        self.area_name = area_name

        # Loading coordinates in a json string
        coords_dic = {'lat': [x[0] for x in coords],
                      'lng': [x[1] for x in coords]
                      }
        coords = json.dumps(coords_dic)
        self.coords = coords

    def __repr__(self):
        return f"Fence {self.area_name}"
