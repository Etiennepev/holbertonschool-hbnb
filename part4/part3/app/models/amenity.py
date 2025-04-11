from .basemodel import BaseModel
from app import db
from sqlalchemy.orm import validates

class Amenity(BaseModel):
	__tablename__ = 'amenities'

	name = db.Column(db.String(50), nullable=False, unique=True)

	@validates('name')
	def validate_name(self, key, value):
		if not isinstance(value, str):
			raise TypeError("Name must be a string")
		if not value:
			raise ValueError("Name cannot be empty")
		if len(value) > 50:
			raise ValueError("Name must be less than or equal to 50 characters")
		return value
	
	def to_dict(self):
		return {
			'id': self.id,
			'name': self.name
		}
