from app import bcrypt, db
from .basemodel import BaseModel
import re
from sqlalchemy.orm import validates

class User(BaseModel):
    __tablename__ = 'users'
    emails = set()

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    @validates('first_name', 'last_name')
    def validate_first_name(self, key, value):
        if not isinstance(value, str):
            raise TypeError("First name must be a string")
        if len(value) > 50:
            raise ValueError("First name must be less than or equal to 50 characters")
        return value

    @validates('email')
    def validate_email(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Email must be a string")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format")
        if value in User.emails:
            raise ValueError("Email already exists")
        if hasattr(self, "_User__email"):
            User.emails.discard(self.__email)
        User.emails.add(value)
        return value

    @validates('password')
    def validate_password(self, key, value):
        if not isinstance(value, str):
            raise TypeError("Password must be a string")
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return self.hash_password(value)

    @validates('is_admin')
    def validate_is_admin(self, key, value):
        if not isinstance(value, bool):
            raise TypeError("Is Admin must be a boolean")
        return value

    def hash_password(self, password):
        """Hashes the password before storing it."""
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def add_place(self, place):
        """Add an amenity to the place."""
        self.places.append(place)

    def add_review(self, review):
        """Add an amenity to the place."""
        self.reviews.append(review)

    def delete_review(self, review):
        """Add an amenity to the place."""
        self.reviews.remove(review)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }
