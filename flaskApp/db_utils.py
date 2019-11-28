
# Collection of simple functions to do "offline" operations during dev.
#
#


def clean_db():
    from app.models import Listing
    from app import db
    # READ
    all_listings = Listing.query.all()

    # Clean database.
    for l in all_listings:
        db.session.delete(l)
    db.session.commit()

    all_listings = Listing.query.all()

    print('READING ALL LISTINGS (should be empty): ', all_listings)
    
def update_fences():
    from app.models import Listing, Fence
    from app import db
    from shapely.geometry import Point
    from shapely.geometry.polygon import Polygon
    import json
    
    # Create all geofences we want to check against.
    fences = []
    for fence in Fence.query.all():
        name = fence.area_name
        coords = json.loads(fence.coords)
        lats, lons = coords['lat'], coords['lon']
        Pol = Polygon(list(zip(lats, lons)))
        fences.append((name, Pol))
    
    # Redo check against all fences. Assuming that fences are non-overlapping for now.
    for listing in Listing.query.all():
        listing_point = Point(float(listing.lat), float(listing.lng))
        
        for fence_name, Pol in fences:
            fence_check = fence_name if listing_point.within(Pol) else None
            
        listing.geofence = fence_check
        db.session.commit()
        print(f'Updated geofence for listing {listing.centris_id}')

def extract_features():
    # Used to update table after exposing some features on the top level.
    import json
    from app.models import Listing
    from app import db
    import re
    
    for listing in Listing.query.all():
        features = json.loads(listing.features)
        
        residential_units = None
        commercial_units = None
        if features.get('Nombre d’unités'):
            for s in features.get('Nombre d’unités').split(","):
                # Matching for residentiel 
                search = re.search(r'r?sid.*\s\(([0-9])\)', s, re.IGNORECASE)
                if search:
                    residential_units = search.group(1)
                # Matching for commercial
                search = re.search(r'mmer.*\(([0-9])\)', s, re.IGNORECASE)
                if search:
                    commercial_units = search.group(1)
                    
        unites_residentielles = features.get('Unités résidentielles')
        unite_principale = features.get('Unité principale')
        
        listing.residential_units = residential_units
        listing.commercial_units = commercial_units
        listing.unites_residentielles = unites_residentielles
        listing.unite_principale = unite_principale
        print(f'updated listing #{listing.centris_id}')
        db.session.commit()

        