from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import config

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()

from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns
from app.api.v1.protected import api as protected_ns

def create_app(config_class=config.DevelopmentConfig):
    # Création de l'application
    app = Flask(__name__)
        
    app.config.from_object(config_class)
    
    # Initialisation des extensions
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    
    # Configuration de l'API
    authorizations = {
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        }
    }
    
    # Initialiser l'API
    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API', authorizations=authorizations)

    # Ajouter les namespaces pour l'API
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(protected_ns, path='/api/v1/protected')

    return app
