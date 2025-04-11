from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Unauthorized')
    @jwt_required()
    @api.doc(security='apikey')
    def post(self):
        """Register a new review"""
        current_user = get_jwt_identity()
        review_data = api.payload
        try:
            new_review = facade.create_review(review_data, current_user)
            return new_review.to_dict(), 201
        except Exception as e:
            return {"error": str(e).strip("'")}, 400

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        return [review.to_dict() for review in facade.get_all_reviews()], 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review.to_dict(), 200

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @jwt_required()
    @api.doc(security='apikey')
    def put(self, review_id):
        """Update a review's information"""
        current_user = get_jwt_identity()
        is_admin = get_jwt()['is_admin']
        review_data = api.payload
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        
        if review.user.id != current_user and not is_admin:
            return {'error': 'Forbidden'}, 403
        try:
            updated_review = facade.update_review(review_id, review_data)
            return updated_review.to_dict(), 200
        except Exception as e:
            return {'error': str(e).strip("'")}, 400

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden')
    @api.doc(security='apikey')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review"""
        current_user = get_jwt_identity()
        is_admin = get_jwt()['is_admin']
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        
        if review.user.id != current_user and not is_admin:
            return {'error': 'Forbidden'}, 403
        try:
            facade.delete_review(review_id)
            return {'message': 'Review deleted successfully'}, 200
        except Exception as e:
            return {'error': str(e).strip("'")}, 400
