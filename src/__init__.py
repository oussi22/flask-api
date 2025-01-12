import os

from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from src.auth import auth
from src.decisions import decisions
from src.database import db


def create_app(test_config=None):
    
    app = Flask(__name__,
                instance_relative_config=True)
    
    app.config["API_TITLE"] = "Cour de Cassation API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    api = Api(app)
    
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
            API_TITLE="Cour de Cassation API"

        )
    else:
        app.config.from_mapping(test_config)
    
    
    db.app = app
    db.init_app(app)

    JWTManager(app)


    api.register_blueprint(auth)
    api.register_blueprint(decisions)

  
    return app