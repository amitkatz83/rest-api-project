import os 
from flask import Flask #import flask and request class
from flask_smorest import Api
from db import db
from blocklist import BLOCKLIST
from flask_migrate import Migrate
import models
import secrets
#import the blueprint classes 
from resources.item import blp as ItemBluePrint
from resources.store import blp as StoreBluePrint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from flask_jwt_extended import JWTManager
from flask import Flask, jsonify
from dotenv import load_dotenv #for load .env file
from rq import Queue
import redis


#create function to run the application
def create_app(db_url=None):
     
    #to run the application
    app=Flask(__name__)
    load_dotenv() #to load .env file 

    #deal with redis
    connection=redis.from_url(os.getenv("REDIS_URL")) #get the redis queue
    app.queue=Queue("emails",connection=connection) #connect to queue
    
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    #define DB
    app.config["SQLALCHEMY_DATABASE_URI"]=db_url or os.getenv("DATABASE_URL","sqlite:///data.db") #the connection string to DB
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False #to makre sure app runs faster
    db.init_app(app)  #initizalise the program with DB
    migrate = Migrate(app, db) #migrate between app and DB.
    api=Api(app)

    #configure sectret key 
    app.config["JWT_SECRET_KEY"]="161896573359112828208907735759987471406" #secrets.SystemRandom().getrandbits(128) #would restart 
    #create JWT manager object 
    jwt = JWTManager(app) #connect the app to jwt manger    
    
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header,jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST  #check if the token is revoked

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity==1: #meaning its the first user in the system 
            return {"is admin": True }
        return {"is admin": False }
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )
    
    #error handeling fresh token
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )


    #handeling expired token 
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )
    #handeling invalid token 
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )
    #handeling not autherized token 
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @app.before_first_request #on start request launched we create the tables 
    def create_tables():
       db.create_all() #create the tables

    api.register_blueprint(ItemBluePrint)
    api.register_blueprint(StoreBluePrint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    return app