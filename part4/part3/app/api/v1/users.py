from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user'),
    'is_admin': fields.Boolean(description='Admin status of the user', default=False)
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    @jwt_required(optional=True)
    def post(self):
        """Register a new user"""
        user_data = api.payload

        if 'is_admin' in user_data:
            user = get_jwt_identity()
            if not user:
                return {'error': 'Unauthorized'}, 401
            is_admin = get_jwt()['is_admin']
            print(is_admin)
            if not is_admin:
                return {'error': 'Forbidden'}, 403

        # Simulate email uniqueness check (to be replaced by real validation with persistence)
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400

        try:
            new_user = facade.create_user(user_data)
            return {'message': 'User successfully created', 'id': new_user.id}, 201
        except Exception as e:
            return {'error': str(e).strip("'")}, 400
        
    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve a list of users"""
        users = facade.get_users()
        return [user.to_dict() for user in users], 200
    
@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @api.expect(user_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @api.doc(security='apikey')
    @jwt_required()
    def put(self, user_id):
        current_user = get_jwt_identity()
        admin = get_jwt()['is_admin']
        
        if current_user != user_id and not admin:
            return {'error': 'Forbidden'}, 403
        
        user_data = api.payload
        if not admin and user_data.get('is_admin'):
            return {'error': 'Forbidden'}, 403

        if not admin and (user_data.get('email') or user_data.get('password')):
            return {'error': 'You cannot modify email or password.'}, 400
        
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        try:
            facade.update_user(user_id, user_data)
            return user.to_dict(), 200
        except Exception as e:
            return {'error': str(e).strip("'")}, 400
