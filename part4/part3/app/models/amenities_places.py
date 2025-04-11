from app import db

class AmenityPlace(db.Model):
    __tablename__ = 'amenities_places'

    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), primary_key=True)
    amenity_id = db.Column(db.String(36), db.ForeignKey('amenities.id'), primary_key=True)
