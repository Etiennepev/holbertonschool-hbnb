from .basemodel import BaseModel
from app import db
from sqlalchemy.orm import validates

class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    amenities = db.relationship('Amenity', secondary='amenities_places', backref='places', lazy='dynamic')

    owner = db.relationship('User', backref='places', lazy='select')

    @validates('title')
    def validate_title(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        if 10 < len(value) > 100:
            raise ValueError("Title must be between 10 and 100 characters")
        return value
    
    @validates('description')
    def validate_description(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Description must be a string")
        if len(value) > 500:
            raise ValueError("Description must be less than or equal to 500 characters")
        return value
    
    @validates('price')
    def validate_price(self, key, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError("Price must be a float")
        if value <= 0:
            raise ValueError("Price must be positive.")
        return value
    
    @validates('latitude')
    def validate_latitude(self, key, value):
        if not isinstance(value, float):
            raise TypeError("Latitude must be a float")
        if not -90 <= value <= 90:
            raise ValueError("Latitude must be between -90 and 90.")
        return value
    
    @validates('longitude')
    def validate_longitude(self, key, value):
        if not isinstance(value, float):
            raise TypeError("Longitude must be a float")
        if not -180 <= value <= 180:
            raise ValueError("Longitude must be between -180 and 180.")
        return value

    def add_review(self, review):
        """Add a review to the place."""
        self.reviews.append(review)
    
    def delete_review(self, review):
        """Add an amenity to the place."""
        self.reviews.remove(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        self.amenities.append(amenity)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.owner.id
        }
    
    def to_dict_list(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner': self.owner.to_dict(),
            'amenities': self.amenities,
            'reviews': self.reviews
        }
