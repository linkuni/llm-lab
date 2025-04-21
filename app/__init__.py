from flask import Flask
from flask_cors import CORS
from app.extensions import init_extensions
from app.config import config_by_name

def create_app(config_name="development"):
    """
    Application factory function that creates and configures the Flask app
    """
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGIN"]}})
    
    # Register blueprints
    from app.api.v1.routes import api_v1
    app.register_blueprint(api_v1)
    
    return app 