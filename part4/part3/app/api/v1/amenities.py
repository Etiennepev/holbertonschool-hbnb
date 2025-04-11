from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade


api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @api.doc(security='apikey')
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if not current_user:
            return {'error': 'Unauthorized'}, 401
        is_admin = get_jwt()['is_admin']
        print(current_user, is_admin)
        if not is_admin:
            return {'error': 'Forbidden'}, 403
        """Register a new amenity"""
        amenity_data = api.payload
        
        existing_amenity = facade.amenity_repo.get_by_attribute('name', amenity_data.get('name'))
        if existing_amenity:
            return {'error': 'Invalid input data'}, 400
        try:
            new_amenity = facade.create_amenity(amenity_data)
            return new_amenity.to_dict(), 201
        except Exception as e:
            return {'error': str(e).strip("'")}, 400

    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve a list of all amenities"""
        amenities = facade.get_all_amenities()
        return [amenity.to_dict() for amenity in amenities], 200


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return amenity.to_dict(), 200

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @api.doc(security='apikey')
    @jwt_required()
    def put(self, amenity_id):
        current_user = get_jwt_identity()
        if not current_user:
            return {'error': 'Unauthorized'}, 401
        is_admin = get_jwt()['is_admin']
        if not is_admin:
            return {'error': 'Forbidden'}, 403
        amenity_data = api.payload
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        try:
            updated_amenity = facade.update_amenity(amenity_id, amenity_data)
            return updated_amenity.to_dict(), 200
        except Exception as e:
            return {'error': str(e).strip("'")}, 400
