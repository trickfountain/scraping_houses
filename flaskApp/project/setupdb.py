from db_setup import db, Listing

db.create_all()

listing1 = Listing("11269851", 'Condo', "764000", "detailed_link",
                 "broker_link", "45.487688", "-73.636512")

db.session.add_all([listing1])
db.session.commit()

print(listing1.id)